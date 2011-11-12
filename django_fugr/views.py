from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

@login_required
def index(request):
	return direct_to_template(request, "index.html", {})

