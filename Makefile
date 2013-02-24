all:
	coffee -co assets/js coffee

watch:
	coffee -wco assets/js coffee > /dev/null
