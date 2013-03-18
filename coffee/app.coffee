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

randomInt = (min, max) -> min + Math.floor(Math.random() * (max-min))
d6 = -> randomInt(1, 7)
_3d6CumProbs = [0.46, 1.85, 4.62, 9.25, 16.20, 25.92, 37.50, 50.00, 62.50, 74.07, 83.79, 90.74, 95.37, 98.14, 99.53, 100]

evalModifiers = (str) ->
	if 0 <= str.indexOf '+'
		parseInt str.split('+')[0] + parseInt str.split('+')[1]
	if 0 <= str.indexOf '-'
		parseInt str.split('-')[0] - parseInt str.split('-')[1]
	parseInt str


App.SuccessRollView = Ember.View.extend
	templateName: 'success-roll'
	tagName: 'button'

	successRate: (->
			if 3 <= evalModifiers(@target) <= 18
				return _3d6CumProbs[evalModifiers(@target) - 3] + '%'
			if 3 > evalModifiers(@target)
				return '0%'
			'100%'
		).property 'target'

	successStyle: (->
			if 3 <= evalModifiers(@target) <= 18
				p = _3d6CumProbs[evalModifiers(@target) - 3]
				'color: ' + (if p < 50 then 'red' else if p < 80 then 'orange' else 'green')
		).property 'target'

	click: -> popup App.RollResultView.create(roll: d6() + d6() + d6() - evalModifiers(@target))

popup = (view) ->
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

App.RollResultView = Ember.View.extend
	templateName: 'roll-result'

	rollString: (->
			if @roll <= 0 then @roll else '+' + @roll
		).property 'roll'
	successStyle: (->
			'color: ' + (if @roll <= 0 then 'green' else 'red')
		).property 'roll'

loadcss = (css) ->
	$("<link/>",
		rel: "stylesheet",
		type: "text/css",
		href: "/css/" + css
	).appendTo "head"
