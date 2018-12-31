# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from functools import wraps
from django.utils import six
from django.utils.decorators import available_attrs
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from libs.user import userissuperuser


def perm_required(perm):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, if not the PermissionDenied exception is raised.
    """
    def _method_wrapper(view_method):
        @wraps(view_method)
        def _arguments_wrapper(request, *args, **kwargs):
            if isinstance(perm, six.string_types):
                perms = (perm,)
            else:
                perms = perm
            # First check if the user has the permission (even anon users)
            if request.user.has_perms(perms):
                return view_method(request, *args, **kwargs)
            # In case the 403 handler should be called raise the exception
            raise PermissionDenied
            # As the last resort, show the login form
        return _arguments_wrapper
    return _method_wrapper


def any_perm_required(perm, *argv):
    """
    Decorator for views that checks whether a user has any selected permission
    enabled, if not the PermissionDenied exception is raised.
    """
    def _method_wrapper(view_method):
        @wraps(view_method)
        def _arguments_wrapper(request, *args, **kwargs):
            if isinstance(perm, six.string_types):
                perms = (perm,)
            else:
                perms = perm
            if len(argv):
                perms += tuple([p for p in argv])
            # First check if the user has any of the permission
            for p in perms:
                if request.user.has_perm(p):
                    return view_method(request, *args, **kwargs)
            # In case the 403 handler should be called raise the exception
            raise PermissionDenied
            # As the last resort, show the login form
        return _arguments_wrapper
    return _method_wrapper


def module_perms_required(applabel):
    """
    Decorator for views that checks whether a user has a any module permission
    enabled, if not the PermissionDenied exception is raised.
    """
    def _method_wrapper(view_method):
        @wraps(view_method)
        def _arguments_wrapper(request, *args, **kwargs):
            # First check if the user has any of the permission
            if request.user.has_module_perms(applabel):
                return view_method(request, *args, **kwargs)
            # In case the 403 handler should be called raise the exception
            raise PermissionDenied
            # As the last resort, show the login form
        return _arguments_wrapper
    return _method_wrapper


def checkissuperuser(raise_exception=True):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if userissuperuser(request):
                return view_func(request, *args, **kwargs)
            if raise_exception:
                raise PermissionDenied
            return redirect('login')
        return _wrapped_view
    return decorator


def userissuperuser_required(raise_exception=True):
    return checkissuperuser(raise_exception=raise_exception)
