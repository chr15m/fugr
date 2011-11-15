from xml.dom.minidom import parseString, Node, Element

def parse_opml(xml):
	""" Uses minidom to extract relevant feed info and labels from the opml file. """
	opml = parseString(xml)
	structure = {}
	parentlabels = set()
	recurse_outlines(opml.getElementsByTagName("body")[0], structure, parentlabels)
	return structure

def recurse_outlines(parent, structure, parentlabels):
	""" Recurses down into an outline node finding other outline nodes and treating it as a label if it has no feed url. """
	for c in parent.childNodes:
		if isinstance(c, Element) and c.tagName == "outline":
			title = c.getAttribute("title") or c.getAttribute("text")
			feed_url = c.getAttribute("xmlUrl")
			blog_url = c.getAttribute("htmlUrl")
			# this is just a heirarchical label
			if feed_url:
				labels = set()
				if structure.has_key(feed_url):
					structure[feed_url]["labels"] = structure[feed_url]["labels"].union(parentlabels)
				else:
					structure[feed_url] = {"title": title, "blog_url": blog_url, "labels": parentlabels}
			else:
				labels = set([title])
			recurse_outlines(c, structure, parentlabels.union(labels))

# run it on the command line
if __name__ == "__main__":
	from sys import argv
	from pprint import pprint
	if len(argv) == 2:
		pprint(parse_opml(file(argv[1]).read()))
	else:
		print "Usage: ", argv[0], "opml-file.xml"

