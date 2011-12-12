def generate_internal_feed(request, username, filter_name, *tags):
	print user, filter_name, tags
	# TODO: check if this user wants their stuff private?
	user = get_object_or_404(User, username=username)
	pass

def filter_all():
	pass

def filter_interesting():
	pass

def filter_popular():
	pass

