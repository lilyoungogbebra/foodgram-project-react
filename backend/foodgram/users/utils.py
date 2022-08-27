def user_is_subscribed(self, obj):
    user = self.context['request'].user
    return (
        user.is_authenticated
        and obj.subscribing.filter(user=user).exists()
    )
