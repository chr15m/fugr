$(function(){
	var MAX_AT_ONCE = 10;
	
	// global object holding all data about the current user's session
	var session = {
		"tags": {},
		"feeds": {},
		"current_feed": null,
		"username": username,
	};
	
	// this header will hang out at the top of the read area
	function set_header(title, backfunc) {
		var headerhtml = $("<div class='read-header ui-state-default'></div>");
		// add the title they requested
		if (typeof(title) != "undefined") {
			headerhtml.append("<span class='title'>" + title + "</span>");
		}
		// if there is a backfunc callback
		if (backfunc) {
			headerhtml.append($("<button id='read-back' class='ui-widget ui-button headerbutton'><span class='ui-icon ui-icon-circle-arrow-w'></span></button>").click(function(e) {
				backfunc();
			}));
		}
		// refresh button
		headerhtml.append("<button id='read-refresh' class='ui-widget ui-button headerbutton'><span class='ui-icon ui-icon-arrowrefresh-1-e'></span></button>");
		$('div#tab-read').html(headerhtml);
		// turn those things into jquery ui buttons
		$('button.headerbutton').button();
	}
	
	// puts the loading spinner in the header area
	function show_spinner() {
		$("div#tab-read").html("<img src='/media/img/loader.gif' id='loader'/>");
	}
	
	// jquery-ui styles
	$('.tabs').tabs();
	$('button,input[type=submit]').button();
	$('input').addClass('ui-widget');
	
	// upload an OPML file
	$('button#upload-opml').click(function(e){
		$('input#opml-upload').trigger("click");
	});
	
	// when the file field is changed submit this thing automatically
	$('input[type=file]').change(function() {
		// TODO: progressbar feedback as we upload
		$('form#opml-upload').submit();
	});
	
	// loads a particular feed into the read area
	function load_feed(feed, backfunc) {
		// show spinner while we load
		show_spinner();
		$.get("/fugr/json/feed/" + escape(feed.url),
			function(feed_json) {
				session.current_feed = feed_json;
				set_header("<a href='" + feed_json.feed.link + "'>" + feed_json.feed.title + "</a>", backfunc);
				var feedcontainer = $("<div></div>");
				// TODO: paginate this properly
				for(var i = 0; i < feed_json.entries.length && i < MAX_AT_ONCE; i++) {
					var entry = feed_json.entries[i];
					//console.log(entry);
					// entry.link
					// entry.title
					// entry.updated
					// entry.content[0].value
					var entryheader = $("<h3><a href='#'>" + entry.title + "</a></h3><div>" + (typeof(entry.content) != "undefined" ? entry.content[0].value : entry.summary ) + "</div>");
					feedcontainer.append(entryheader);
				}
				$('div#tab-read').append(feedcontainer);
				feedcontainer.accordion({"collapsible": true, "autoHeight": false, "clearStyle": true, "active": false});
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
				load_feed(feed, function() { populate_read_tab_with_feeds(tagname, backfunc); });
			}
		}
		// add the link to summary feeds
		$("div#tab-read").append($("<div class='feed-link feedlist' id='feed-link-all'>" + tagname + " - All</div>").click(make_load_func("/feeds/" + session.username + "/" + tagname)));
		$("div#tab-read").append($("<div class='feed-link feedlist' id='feed-link-all'>" + tagname + " - Interesting</div>").click(make_load_func("/feeds/" + session.username + "/interesting/" + tagname)));
		var tagfeeds = session.tags[tagname];
		// now put the feeds in there
		if (typeof tagfeeds != "undefined") {
			for (var f=0; f<tagfeeds.length; f++) {
				$("div#tab-read").append(
					$("<div class='feed-link feedlist'>" + tagfeeds[f].title + "</div>").click(make_load_func(tagfeeds[f]))
				);
			}
		}
		// add the folder icons
		$("div.feed-link").addClass("ui-state-default");
		$("div.feed-link").prepend("<span class='ui-icon ui-icon-signal-diag'></span>");
		// make them clickable
		$("div.feed-link");
	}
	
	// populates the read tab with this user's tags
	function populate_read_tab_with_tags(tags) {
		// empty the area
		set_header("All Tags", false);
		// default 'tag' links
		$("div#tab-read").append($("<div class='feedtag-link feedlist'>All Items</div>"));
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
