App = Ember.Application.create
	LOG_TRANSITIONS: true

Ember.LOG_BINDINGS = true

App.Router.map ->
	@resource 'sheets'
	@resource 'sheet', path: '/sheets/:sheet_id'

App.IndexRoute = Ember.Route.extend
	redirect: -> @transitionTo 'sheets'

App.SheetsController = Ember.ArrayController

App.SheetsRoute = Ember.Route.extend
	setupController: (controller) ->
		$.get 'sheets', (data) ->
			controller.set 'content', data

App.SheetRoute = Ember.Route.extend
	model: (params) -> id: params.sheet_id
	setupController: (controller, model) ->
		$.get "sheets/#{model.id}", (data) ->
			controller.set 'content', data
