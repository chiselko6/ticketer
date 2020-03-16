HEROKU_REMOTE=heroku-tg
GIT_REMOTE=ticketer-tg-bot


heroku-bash:
	@heroku run --remote $(HEROKU_REMOTE) bash

heroku-ps:
	@heroku ps --remote $(HEROKU_REMOTE)

heroku-push:
	@git push $(HEROKU_REMOTE) $(shell git rev-parse --abbrev-ref HEAD):master -f

heroku-logs:
	@heroku logs --remote $(HEROKU_REMOTE)
