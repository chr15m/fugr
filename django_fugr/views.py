from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from parse_opml import parse_opml

@login_required
def index(request):
	return direct_to_template(request, "index.html", {})

@login_required
def opml_upload(request):
	uploaded = request.FILES.get('opml-upload')
	if uploaded:
		opmldata = parse_opml(uploaded.read())
		# create or modify feed objects for this opml data
		uploaded.close()
	from pprint import pformat
	return HttpResponse(pformat(opmldata), mimetype="text/plain")
	#return HttpResponseRedirect(reverse("index"))

