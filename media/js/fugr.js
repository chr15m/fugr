$(function(){
	// global object holding all data about the current user's session
	var session = {
		"tags": {},
		"feeds": {}
	};
	
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
	
	// populates the read tab with this user's tags
	function populate_read_tab_with_tags(tags) {
		// empty the area
		$("div#tab-read").html("");
		// default 'tag' links
		$("div#tab-read").append($("<div class='feedtag'>All Items</div>"));
		$("div#tab-read").append($("<div class='feedtag'>Read Items</div>"));
		$("div#tab-read").append($("<div class='feedtag'>Starred Items</div>"));
		$("div#tab-read").append($("<div class='feedtag'>People You Follow</div>"));
		//$("div#tab-read").append($("<div class='feedtag'>Recommended Items</div>"));
		// now put the tags in there
		for (var tag in tags) {
			var tagdiv = $("<div class='feedtag'>" + tag + "</div>");
			$("div#tab-read").append(tagdiv);
		}
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
