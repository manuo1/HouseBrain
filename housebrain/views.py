from datetime import datetime

from django.shortcuts import render

def homepage(request):
    context = {'date_time': f'{datetime.now():%d/%m/%Y %H:%M}'}
    return render(request, 'homepage.html', context)
