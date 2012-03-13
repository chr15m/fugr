$(function(){
	/***** style *****/
	
	// on mobile devices make the font size a bit more readable
	if ((/android|ipad|iphone/gi).test(navigator.appVersion)) {
		$("body").css({"font-size": ".9em"});
	}
		
	// jquery-ui styles
	$('.tabs').tabs();
	$('button,input[type=submit]').button();
	$('input').addClass('ui-widget');

	/***** global/utility stuff *****/
	
	// global object holding all data about the current user's session
	var session = {
		"tags": {},
		"feeds": {},
		"current_feed": null,
		"username": username,
	};
	
	// puts the loading spinner in the header area
	function show_spinner() {
		$("div#tab-read").html("<img src='/media/img/loader.gif' id='loader'/>");
	}

	/***** OPML upload *****/
	
	// continually hit the opml-progress URL to see how far through the upload/parse we are
	function check_opml_progress(dialog, progress, progress_message) {
		// launch the ajax request to check
		$.get("/fugr/opml-progress", function(result) {
			// update UI with what we now know
			progress.progressbar({"value": result.value * 100});
			var log = result.log.split("\n");
			progress_message.text(log[log.length - 1]);
			// keep checking
			setTimeout(function() { check_opml_progress(dialog, progress, progress_message) }, 100);
		}, "json");
	}
	
	// upload an OPML file
	$('button#upload-opml').click(function(e){
		// when the file field is changed
		$("#opml-upload-frame").contents().find('input[type=file]').change(function() {
			// reset the progress counter before we start
			$.get("/fugr/opml-progress?reset=1");
			
			// when the frame has finished loading we want to know about it
			function post_frame_loaded() {
				// find the word 'true' in the frame
				if ($("#opml-upload-frame").contents().text().indexOf("true") != -1) {
					// reload the page
					document.location.href = "/";
				}
			}
			$("#opml-upload-frame").load(post_frame_loaded);
			$("#opml-upload-frame").ready(post_frame_loaded);
			
			// show the progress bar and update it continuously
			var progress = $('<div></div>').progressbar();
			var progress_message = $('<p></p>');
			var dialog = $('<div title="OPML Upload"></div>').append(progress_message).append(progress).dialog({"width": Math.max(300, $(window).width() / 3)});
			check_opml_progress(dialog, progress, progress_message);
			
			// do the submit
			$("#opml-upload-frame").contents().find("form#opml-upload").submit();
		});
		
		// trigger a click so that the user can choose a file
		$("#opml-upload-frame").contents().find("input#opml-upload").trigger("click");
	});
	
	/***** interactively flagging entries *****/
	
	// different types of update we can register with the server
	update_types = {
		"like": ['Like this article', "heart"],
		"star": ['Star this article', "star"],
		"read": ['Read/Unread article', "check"]
	};
	
	// updates an entry with the user action (e.g. mark read, like, star)
	function update_entry(which, entry, update_type, header_element, forcevalue) {
		// URL = /update_type/value/uid
		// which = originating element
		// update_type = "read", "like", "star"
		// uid = uid of the entry
		
		var inner = $(which).find("span.ui-button-text span");
		var spinner = $("<img src='media/img/loader-small.gif'/>").css({
			"float": "left",
			"padding": "0px",
			"margin": "0px"
		});
		inner.html(spinner);
		var obg = inner.css("background-image");
		inner.css({"background-image": "none"});
		$(which).removeClass("ui-state-hover");
		$(which).removeClass("ui-state-focus");
		if (typeof(forcevalue) == "undefined") {
			var value = !$(which).hasClass("ui-state-highlight");
		} else {
			var value = forcevalue;
		}
		var uid = entry.id;
		//console.log(value, uid);
		// send ajax request
		$.get("/fugr/update-entry/" + update_type + "/" + value + "?uid=" + encodeURIComponent(uid), function(result) {
			if (result["fields"]) {
				// stop the spinner from happening
				spinner.remove();
				if (result["fields"][update_type] == null) {
					$(which).removeClass("ui-state-highlight");
					$(which).addClass("ui-state-default");
					if (update_type == "read") {
						$(header_element).removeClass("read-entry");
					}
				} else {
					$(which).removeClass("ui-state-default");
					$(which).addClass("ui-state-highlight");
					if (update_type == "read") {
						$(header_element).addClass("read-entry");
					}
				}
				inner.css({"background-image": ""});
			}
		}, "json");
		//inner.addClass("ui-state-active");
	}
	
	/***** browsing and reading feeds *****/
	
	// this header will hang out at the top of the read area
	function set_header(title, backfunc) {
		var headerhtml = $("<div class='read-header ui-state-default'></div>");
		// if there is a backfunc callback
		if (backfunc) {
			headerhtml.append($("<button id='read-back' class='ui-widget ui-button headerbutton'><span class='ui-icon ui-icon-circle-arrow-w'></span></button>").click(function(e) {
				backfunc();
			}));
		}
		// refresh button
		headerhtml.append("<button id='read-refresh' class='ui-widget ui-button headerbutton'><span class='ui-icon ui-icon-arrowrefresh-1-e'></span></button>");
		// add the title they requested
		if (typeof(title) != "undefined") {
			headerhtml.append("<span class='title'>" + title + "</span>");
		}
		$('div#tab-read').html(headerhtml);
		// turn those things into jquery ui buttons
		$('button.headerbutton').button();
	}
	
	// loads a particular feed into the read area
	function populate_read_tab_with_feed(feed_url, backfunc) {
		// show spinner while we load
		show_spinner();
		// first fetch the feed we want
		$.get("/fugr/json/feed?url=" + encodeURIComponent(feed_url),
			function(feed_json) {
				if (feed_json == null) {
					// fake it
					feed_json = {"feed": {"link": "", "title": "No data"}, "entries": []};
				}
				session.current_feed = feed_json;
				set_header("<a href='" + feed_json.feed.link + "'>" + feed_json.feed.title + "</a>", backfunc);
				var feedcontainer = $("<div></div>");
				// add all entries we fetch from the server to the reading area (collapsed)
				for(var i = 0; i < feed_json.entries.length; i++) {
					var entry = feed_json.entries[i];
					//console.log(entry);
					// entry.link
					// entry.title
					// entry.updated
					// entry.content[0].value
					// TODO: if there are multiple content parts show them all
					// TODO: check if content parts are some other mimetype like mp3 or whatever
					// strip HTML from summary -> http://robertnyman.com/roblab/javascript-remove-tags.htm
					var entryheader = $(
						"<h3 class='entry" + (entry.read == null ? "" : " read-entry") + "'>" +
						"<a href='#'>" + entry.title + "</a>" +
						"<div class='entry-summary'>" +
						// put the feed title in there if we are doing an aggregated feed
						(feed_url.indexOf("/feeds") == 0 ? (entry["feed_names"] ? entry.feed_names[0] + " - " : entry.author + " - ") : "") + 
						// summarise the entry in the header
						(entry["summary"] ? entry.summary : (entry["content"] ? entry.content[0].value : "")).replace(/<\/?[^>]+(>|$)/g, "").substr(0, 100) +
						"...</div>" +
						"</h3><div class='feedcontent' entry_id='" + i + "'></div>");
					feedcontainer.append(entryheader);
				}
				// add a 'more' button here
				// now add all the HTML we just generated to the container we created for viewing
				$('div#tab-read').append(feedcontainer);
				// make the collapsed entries accordion out with their content when the user taps them
				feedcontainer.accordion({
					"collapsible": true,
					"autoHeight": false,
					"clearStyle": true,
					"active": false,
					// ### when the user taps an entry header ### //
					"change": function(ev, ui) {
						var dest = $(ui.newContent);
						// get the entry data for this element
						var entry = feed_json.entries[parseInt(dest.attr("entry_id"))];
						if (entry) {
							// create the entry flagging buttons (like, read, etc.) at the top
							var buttons = $("<div></div>");
							for (t in update_types) {
								function make_update_entry_function(which, entry_in, type, header_element) {
									return function(){ update_entry(this, entry_in, type, header_element); }
								}
								var btnhtml = "<button class='ui-widget ui-button " + t + "-button' title='" +
									update_types[t][0] + "'><span class='ui-icon ui-icon-" + update_types[t][1] + "'></span></button>";
								var btn = $(btnhtml).button().click(make_update_entry_function(this, entry, t, ui.newHeader));
								if (entry[t] != null) {
									btn.addClass("ui-state-highlight");
									btn.removeClass("ui-state-default");
								} else if (t == "read") {
									// always mark this as read when we first read it if not already marked
									update_entry(btn, entry, "read", ui.newHeader, true);
								}
								buttons.append(btn);
							}
							
							// add the button bar to the entry
							dest.html($("<div class='feedbuttons'></div>").prepend(buttons));
							var content = $(
								"<div class='top-line'>" +
								"<span class='entry-author'>" + (entry["author"] ? entry.author + " - " : "") + "</span>" +
								"<a href='" + entry.link + "' target='_new' class='entry-original-link'>original article</a>" +
								"<span class='entry-date'>" + entry.updated_parsed.replace("T", " ") + "</span>" +
								"</div>" +
								"<div class='feedcontent-inner'>" +
								(typeof(entry.content) != "undefined" ? entry.content[0].value : (typeof(entry.summary) != "undefined" ? entry.summary : "")) +
								"</div>"
							);
							// once the images load, make sure they fit the screen
							function imgresize(ev, el) {
								var el = el ? el : this;
								if ($(el).width() > content.width()) {
									// HACK - TODO: fix this to account for margins
									// TODO: re-do this on resize event too
									// NOTE: also ignore ads
									var ratio = 1.0 * $(el).width() / $(el).height();
									$(el).width(content.width());
									$(el).height(content.width() / ratio);
									$(el).css({
										"margin-left": "-0.5em",
									});
								}
							}
							content.find("img").load(imgresize);
							$(window).resize(function() {
								content.find("img").each(function(i, el) {
									imgresize(null, el);
								});
							});
							dest.append(content);
							// TODO: make this work - buttons along the bottom of the article too
							// dest.append(bar.clone());
							// scroll to the new entry we just tapped on
							$('html, body').scrollTop(dest.prev().offset().top);
						} else {
							dest.append("Fugr error - entry not found.");
						}
					}
				});
				window.scrollTo(0,1);
			},
			"json"
		);
	}
	
	// populates the read tab with this tag's feeds
	function populate_read_tab_with_feeds(tagname, backfunc) {
		// empty the area
		set_header(tagname, backfunc);
		// function factory to load the feed
		function make_load_func(feed) {
			return function(e) {
				populate_read_tab_with_feed(feed, function() { populate_read_tab_with_feeds(tagname, backfunc); });
			}
		}
		// add the link to summary feeds
		$("div#tab-read").append($("<div class='feed-link feedlist' id='feed-link-all'>" + tagname + " - All</div>").click(make_load_func("/feeds/" + session.username + "/all/" + tagname)));
		$("div#tab-read").append($("<div class='feed-link feedlist' id='feed-link-all'>" + tagname + " - Interesting</div>").click(make_load_func("/feeds/" + session.username + "/interesting/" + tagname)));
		$("div#tab-read").append($("<div class='feed-link feedlist' id='feed-link-all'>" + tagname + " - Popular</div>").click(make_load_func("/feeds/" + session.username + "/popular/" + tagname)));
		var tagfeeds = session.tags[tagname];
		// now put the feeds in there
		if (typeof tagfeeds != "undefined") {
			for (var f=0; f<tagfeeds.length; f++) {
				$("div#tab-read").append(
					$("<div class='feed-link feedlist'>" + tagfeeds[f].title + "</div>").click(make_load_func(tagfeeds[f].url))
				);
			}
		}
		// add the folder icons
		$("div.feed-link").addClass("ui-state-default");
		$("div.feed-link").prepend("<span class='ui-icon ui-icon-signal-diag'></span>");
		window.scrollTo(0,1);
	}
	
	// populates the read tab with this user's tags
	function populate_read_tab_with_tags(tags) {
		// empty the area
		set_header("All Tags", false);
		// default 'tag' links
		$("div#tab-read").append($("<div class='feedtag-link feedlist'>Firehose</div>"));
		$("div#tab-read").append($("<div class='feedtag-link feedlist'>Read Items</div>"));
		$("div#tab-read").append($("<div class='feedtag-link feedlist'>Liked Items</div>"));
		$("div#tab-read").append($("<div class='feedtag-link feedlist'>Starred Items</div>"));
		//$("div#tab-read").append($("<div class='feedtag-link feedlist'>People You Follow</div>"));
		//$("div#tab-read").append($("<div class='feedtag'>Recommended Items</div>"));
		// add the Untagged list at the start
		$("div#tab-read").append("<div class='feedtag-link feedlist'>Untagged</div>");
		// now put the tags in there
		for (var tag in tags) {
			// skip the untagged list
			if (tag != "Untagged") {
				$("div#tab-read").append("<div class='feedtag-link feedlist'>" + tag + "</div>");
			}
		}
		// add the folder icons
		$("div.feedtag-link").addClass("ui-state-default");
		$("div.feedtag-link").prepend("<span class='ui-icon ui-icon-folder-open'></span>");
		// make them clickable
		$("div.feedtag-link").click(function(e) {
			populate_read_tab_with_feeds($(this).text(), function() { populate_read_tab_with_tags(tags); });
		});
		window.scrollTo(0,1);
	}
	
	function add_feed_to_tag(feed_url, data, tagname) {
		// add the feed url to this tuple
		data[feed_url].url = feed_url;
		// if we don't have this tag yet create it as an array
		if (typeof(session.tags[tagname]) == "undefined") {
			session.tags[tagname] = [];
		}
		// push this feed onto the tag it belongs to
		session.tags[tagname].push(data[feed_url]);
	}
	
	/***** liftoff *****/
	
	// load up our list of tags into the main pane
	$.get("/fugr/json/feeds", function(data) {
		session.feeds = data;
		// build the inverse datastructure of what we got - a list of tags pointing to feeds
		for (var feed_url in data) {
			var tags = data[feed_url].tags;
			if (tags.length > 0) {
				// this feed has some tags attached
				for (var t=0; t<tags.length; t++) {
					add_feed_to_tag(feed_url, data, tags[t]);
				}
			} else {
				add_feed_to_tag(feed_url, data, "Untagged");
			}
		}
		// populate the read area with the tags to begin with
		populate_read_tab_with_tags(session.tags);
	}, "json")
});
