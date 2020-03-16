HEROKU_REMOTE=heroku-crawler
GIT_REMOTE=ticketer-crawler


heroku-bash:
	@heroku run --remote $(HEROKU_REMOTE) bash

heroku-ps:
	@heroku ps --remote $(HEROKU_REMOTE)

heroku-push:
	@git push $(HEROKU_REMOTE) $(shell git rev-parse --abbrev-ref HEAD):master -f

heroku-logs:
	@heroku logs --remote $(HEROKU_REMOTE)
