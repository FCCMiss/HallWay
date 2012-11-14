# tasks.py

from celery.task import PeriodicTask
from recipe.models import Recipe, Vote
from celery.task.schedules import crontab
from celery.task import task
from django.contrib.auth.models import User

class ProcessTrendTask(PeriodicTask):
	run_every = crontab(hour=0)
	alpha = 0.8

	def run(self, **kwargs):
		objects = Recipe.objects.all()
		for obj in objects:
			obj.trend_num = float(obj.trend_num) * alpha + float(obj.today_view_num) * (1-alpha)
			obj.today_view_num = 0
			obj.save()


@task(ignore_result=True)
def add_view_num(obj):
	obj.view_num = obj.view_num+1
	obj.today_view_num = obj.today_view_num+1
	obj.save()



@task()
def get_or_create_vote(r, u, s):
	try:
		recipe_object = Recipe.objects.get(pk = r)
		user_object = User.objects.get(pk = u)
		v = Vote.objects.get(recipe = recipe_object, user = user_object)
	except Vote.DoesNotExist:
		v = Vote(recipe = recipe_object, user = user_object, score = s)
		
		recipe_object.cumulative_score = recipe_object.cumulative_score + s
		recipe_object.rating_num = recipe_object.rating_num + 1
		recipe_object.save()
		v.save()
	else:
		old_score = v.score
		v.score = s
		recipe_object.cumulative_score = recipe_object.cumulative_score + s - old_score
		recipe_object.save()
		v.save()
