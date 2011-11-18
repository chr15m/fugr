$(function(){
	// global object holding all data about the current user's session
	var session = {
		"tags": {},
		"feeds": {}
	};
	
	// this header will hang out at the top of the read area
	var headerhtml = $("<div class='read-header ui-state-default'><button id='read-back' class='ui-widget ui-button'><span class='ui-icon ui-icon-circle-arrow-w'></span></button><button id='read-refresh' class='ui-widget ui-button'><span class='ui-icon ui-icon-arrowrefresh-1-e'></span></button></div>");
	
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
	function load_feed(feed_url) {
		$.getFeed({
			url: "/fugr/xml/feed/" + escape(feed_url),
			success: function(feed) {
				$('div#tab-read').html(headerhtml);
				$('div#tab-read').append('<h2>'
				+ '<a href="'
				+ feed.link
				+ '">'
				+ feed.title
				+ '</a>'
				+ '</h2>');
				
				var html = '';
				
				for(var i = 0; i < feed.items.length && i < 5; i++) {
				
					var item = feed.items[i];
					
					html += '<h3>'
					+ '<a href="'
					+ item.link
					+ '">'
					+ item.title
					+ '</a>'
					+ '</h3>';
					
					html += '<div class="updated">'
					+ item.updated
					+ '</div>';
					
					html += '<div>'
					+ item.description
					+ '</div>';
				}
				
				$('div#tab-read').append(html);
			}	
		});

	}
	
	// populates the read tab with this tag's feeds
	function populate_read_tab_with_feeds(tagname) {
		// empty the area
		$("div#tab-read").html(headerhtml);
		// add the link to summary feeds
		$("div#tab-read").append("<div class='feed-link' id='feed-link-all'>All " + tagname + "</div>");
		var tagfeeds = session.tags[tagname];
		// now put the feeds in there
		for (var f=0; f<tagfeeds.length; f++) {
			var feed_url = tagfeeds[f].feed_url;
			// function factory to load the feed
			function make_load_func(feed_url) {
				return function(e) {
					load_feed(feed_url);
				}
			}
			$("div#tab-read").append(
				$("<div class='feed-link'>" + tagfeeds[f].title + "</div>").click(make_load_func(feed_url))
			);
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
		$("div#tab-read").html(headerhtml);
		// default 'tag' links
		$("div#tab-read").append($("<div class='feedtag-link'>All Items</div>"));
		$("div#tab-read").append($("<div class='feedtag-link'>Read Items</div>"));
		$("div#tab-read").append($("<div class='feedtag-link'>Starred Items</div>"));
		//$("div#tab-read").append($("<div class='feedtag-link'>People You Follow</div>"));
		//$("div#tab-read").append($("<div class='feedtag'>Recommended Items</div>"));
		// now put the tags in there
		for (var tag in tags) {
			$("div#tab-read").append("<div class='feedtag-link'>" + tag + "</div>");
		}
		// add the folder icons
		$("div.feedtag-link").addClass("ui-state-default");
		$("div.feedtag-link").prepend("<span class='ui-icon ui-icon-folder-open'></span>");
		// make them clickable
		$("div.feedtag-link").click(function(e) {
			populate_read_tab_with_feeds($(this).text());
		});
	}
	
	// load up our list of tags into the main pane
	$.get("/fugr/json/feeds", function(data) {
		session.feeds = data;
		// build the inverse datastructure of what we got - a list of tags pointing to feeds
		for (var feed_url in data) {
			var tags = data[feed_url].tags;
			for (var t=0; t<tags.length; t++) {
				// add the feed url to this tuple
				data[feed_url].feed_url = feed_url;
				// if we don't have this tag yet create it as an array
				if (typeof(session.tags[tags[t]]) == "undefined") {
					session.tags[tags[t]] = [];
				}
				// push this feed onto the tag it belongs to
				session.tags[tags[t]].push(data[feed_url]);
			}
		}
		// populate the read area with the tags to begin with
		populate_read_tab_with_tags(session.tags);
	}, "json")
});
