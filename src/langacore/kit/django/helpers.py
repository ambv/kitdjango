# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
import django.shortcuts


def redirect(request, link='/', chain=False):
    context = RequestContext(request, {})
    if 'auth__redirect_to' in context:
        link = context['auth__redirect_to']

    if chain:
        if link.rfind('?') != -1:
            link = link + '&redirect_to=%s' % link[:link.rfind('?')]
        else:
            link = link + '?redirect_to=%s' % link 

    return HttpResponseRedirect(link)


def render(request, template_name, context, debug=False):
    if hasattr(settings, 'AUTH_PROFILE_MODULE'):
        if 'user_profile' in context:
            raise KeyError, "langacore.kit.django.helpers.render() doesn't accept contexts with 'user_profile'"
        if 'other_user_profile' in context:
            raise KeyError, "langacore.kit.django.helpers.render() doesn't accept contexts with 'other_user_profile'"
    
        context['user_profile'] = request.user.get_profile() if request.user.is_authenticated() else None 
        context['other_user_profile'] = context['other_user'].get_profile() if 'other_user' in context else None

    if debug:
        for key in context:
            print "context['%s'] = %s (type: %s) (repr: %s)" % (key, str(context[key]), type(context[key]), repr(context[key]))
    return django.shortcuts.render_to_response(template_name, RequestContext(request, context))


class Choice(object):
    global_id = 0

    def __init__(self, description, id=-255):
        self.id = id
        self.desc = description
        self.global_id = Choice.global_id
        Choice.global_id += 1


class Choices(list):
    def __init__(self):
        values = []

        for k, v in self.__class__.__dict__.items():
            if type(v) == Choice:
                 values.append(v)

        values.sort(lambda x, y: x.global_id - y.global_id)

        last_choice_id = 0
        for choice in values:
            if choice.id == -255:
                last_choice_id += 1
                choice.id = last_choice_id
            last_choice_id = choice.id
            self.append((choice.id, choice.desc))


if __name__ == '__main__':
    # crude test
    class Test(Choices):
        white = Choice("White")
        yellow = Choice("Yellow")
        red = Choice("Red")
        green = Choice("Green")
        black = Choice("Black")

    print Test()
    print Test.white.id, Test.white.desc
