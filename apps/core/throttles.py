from rest_framework.throttling import UserRateThrottle


class SuperUserThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        return super().allow_request(request, view)
