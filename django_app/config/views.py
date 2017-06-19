from django.shortcuts import render, redirect


def default(request):
    return redirect('post:post_list')
