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

App.SheetController = Ember.ObjectController.extend
	categories: (-> (key for own key, _ of @content.sheet)).property 'content'

App.CategoryView = Ember.View.extend
	setRealTemplate: (template) ->
		@set 'context', @get "context.sheet.#{@category}"
		@set 'template', template
		@rerender()

	template: (->
			if @get 'context'
				$.ajax
					url: "datahandlers/#{@get 'context.system'}/#{@category}.handlebars"
					success: (template) => @setRealTemplate(Ember.Handlebars.compile template)
					error: () => @setRealTemplate Ember.TEMPLATES['category-view']
			(-> "Loading...")
		).property 'context'

	isArray: (-> Ember.Array.detect(@get 'context')).property 'context'

randomInt = (min, max) -> min + Math.floor(Math.random() * (max-min))
d6 = -> randomInt(1, 7)
_3d6CumProbs = [0.46, 1.85, 4.62, 9.25, 16.20, 25.92, 37.50, 50.00, 62.50, 74.07, 83.79, 90.74, 95.37, 98.14, 99.53, 100]

App.SuccessRollView = Ember.View.extend
	templateName: 'success-roll'
	tagName: 'button'

	successRate: (->
			if 3 <= @target <= 18
				_3d6CumProbs[@target - 3] + '%'
		).property 'target'

	successStyle: (->
			if 3 <= @target <= 18
				p = _3d6CumProbs[@target - 3]
				'color: ' + (if p < 50 then 'red' else if p < 80 then 'orange' else 'green')
		).property 'target'

	click: -> window.alert(@target - d6() - d6() - d6())

loadcss = (css) ->
	$("<link/>",
		rel: "stylesheet",
		type: "text/css",
		href: "/css/" + css
	).appendTo "head"
