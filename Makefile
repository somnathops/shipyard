USER    = mycloudhub
VERSION = $(shell cat VERSION)

build:
	docker build -t $(USER)/expense-backend:$(VERSION)  ./backend
	docker build -t $(USER)/expense-frontend:$(VERSION) ./frontend

push:
	docker push $(USER)/expense-backend:$(VERSION)
	docker push $(USER)/expense-frontend:$(VERSION)

ship: build push
