all: templates
	coffee -co assets/js coffee

watch: templates
	coffee -wco assets/js coffee > /dev/null

#TODO maybe actually compile them to JS?
templates:
	rsync -r --include "*/" --include "*.handlebars" --exclude "*" datahandlers assets/
