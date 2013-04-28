randomInt = (min, max) -> min + Math.floor(Math.random() * (max-min))
d6 = -> randomInt(1, 7)
_3d6CumProbs = [0.46, 1.85, 4.62, 9.25, 16.20, 25.92, 37.50, 50.00, 62.50, 74.07, 83.79, 90.74, 95.37, 98.14, 99.53, 100]

evalModifiers = (str) ->
	if 0 <= str.indexOf '+'
		parseInt str.split('+')[0] + parseInt str.split('+')[1]
	if 0 <= str.indexOf '-'
		parseInt str.split('-')[0] - parseInt str.split('-')[1]
	parseInt str

window.Gurps = Gurps = {}

Gurps.SuccessRollView = Ember.View.extend
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

	click: -> App.popup Gurps.RollResultView.create(roll: d6() + d6() + d6() - evalModifiers(@target))

Gurps.RollResultView = Ember.View.extend
	templateName: 'roll-result'

	rollString: (->
			if @roll <= 0 then @roll else '+' + @roll
		).property 'roll'
	successStyle: (->
			'color: ' + (if @roll <= 0 then 'green' else 'red')
		).property 'roll'
