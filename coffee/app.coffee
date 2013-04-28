App = Ember.Application.create
	LOG_TRANSITIONS: true

window.App = App

Ember.LOG_BINDINGS = true

App.Router.map ->
	@resource 'sheets'
	@resource 'sheet', path: '/sheets/:system_id/:sheet_id'

App.IndexRoute = Ember.Route.extend
	redirect: -> @transitionTo 'sheets'

App.SheetsRoute = Ember.Route.extend
	model: -> {}
	setupController: (controller) ->
		$.get 'sheets', (data) ->
			controller.set 'content', data

App.SheetRoute = Ember.Route.extend
	model: (params) ->
		id: params.sheet_id
		system: params.system_id
	serialize: (model) ->
		sheet_id: model.id
		system_id: model.system
	setupController: (controller, model) ->
		$.get "sheets/#{model.system}/#{model.id}", (data) ->
			loadcss "sheet.css"
			controller.set 'content', data

App.CategoryView = Ember.View.extend
	setRealTemplate: (template) ->
		@set 'template', template
		@rerender()

	template: (->
			$.ajax
				url: "datahandlers/#{@get 'parentView.context.system'}/#{@get 'context.id'}.handlebars"
				success: (template) =>
					@set 'context', @get 'context.data'
					@setRealTemplate(Ember.Handlebars.compile template)
				error: () =>
					@setRealTemplate Ember.TEMPLATES['category-view']
			(-> "Loading...")
		).property 'context'

	isArray: (-> Ember.Array.detect(@get 'context.data')).property 'context'

App.popup = (view) ->
	mask = $('<div></div>')
		.css
			position: 'absolute'
			top: 0
			'z-index': 100
			width: '100%'
			height: $(document).height()
			'text-align': 'center'
		.click(-> mask.remove())
		.appendTo $('body')

	box = $('<div></div>')
		.css
			position: 'fixed'
			'z-index': 101
			top: ($(window).height()) / 2
			width: '100%'
		.click(-> mask.remove())
		.appendTo mask

	view.appendTo box

loadcss = (css) ->
	$("<link/>",
		rel: "stylesheet",
		type: "text/css",
		href: "/css/" + css
	).appendTo "head"
