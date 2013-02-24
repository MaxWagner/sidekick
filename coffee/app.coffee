App = Ember.Application.create
	LOG_TRANSITIONS: true

Ember.LOG_BINDINGS = true

App.Router.map ->
	@resource 'sheets'

App.IndexRoute = Ember.Route.extend
	redirect: -> @transitionTo 'sheets'

App.SheetsController = Ember.ArrayController

App.SheetsRoute = Ember.Route.extend
	setupController: (controller) ->
		$.get 'sheets', (data) ->
			console.debug data
			controller.set 'content', data
