from django import forms

from accounts.models import UserProfile, Account
from store.models import ReviewRating


class ReviewRatingForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']



