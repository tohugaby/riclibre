"""
Referendum's app: tests module for referendum view test
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from referendum.models import Referendum, Category, VoteToken


class ReferendumListViewTestCase(TestCase):
    """
    Test ReferendumListView.
    """
    fixtures = ['test_data.json']

    def test_response_status_200(self):
        """
        Test response status is 200 when user is not authenticated.
        """
        self.client = Client()
        response = self.client.get(reverse('referendum_list'))
        self.assertEqual(response.status_code, 200)


class CategoryViewTestCase(TestCase):
    """
    Test CategoryView.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.category = Category.objects.first()
        self.referendum_list = self.category.referendum_set.all()

    def test_category_filter(self):
        """
        Test category view filters referendum
        """
        self.client = Client()
        response = self.client.get(reverse('category', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(self.referendum_list), list(response.context_data['object_list']))


class MyReferendumsViewTestCase(TestCase):
    """
    Test MyReferendumsView.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.referendum_list = self.user.referendum_set.all()

    def test_authenticated_user_filters_referendums(self):
        """
        Test user referendums view filters referendums.
        """
        self.client = Client()
        self.client.force_login(self.user)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        response = self.client.get(reverse('my_referendums'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(self.referendum_list), list(response.context_data['object_list']))

    def test_anonymous_user_redirect(self):
        """
        Test user referendums view filters referendums.
        """
        self.client = Client()
        response = self.client.get(reverse('my_referendums'))
        self.assertEqual(response.status_code, 302)


class ReferendumDetailViewTestCase(TestCase):
    """
    Test ReferendumDetailView.
    """
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.referendum = Referendum.objects.first()
        self.referendum_not_started = Referendum.objects.filter(event_start__isnull=True).first()
        self.user = self.referendum.creator
        self.permission = Permission.objects.get(codename='is_citizen')
        self.citizen = get_user_model().objects.filter(
            Q(user_permissions=self.permission)).first()

    def test_return_200_when_not_authenticated(self):
        """
        test if view return a 200 status when user is not authenticated.
        :return:
        """
        response = self.client.get(self.referendum.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_return_200_when_authenticated(self):
        """
        test if view return a 200 status when user is authenticated.
        :return:
        """
        self.client.force_login(self.user)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        response = self.client.get(self.referendum.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_redirect_to_vote_view_on_vote_date(self):
        """
        Test rediction on vote date.
        """
        nb_vote_token = VoteToken.objects.count()
        self.client.force_login(self.citizen)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        response = self.client.get(self.referendum.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # TODO: check assertion
        self.assertNotContains(response, "label='Vote'")
        self.referendum_not_started.event_start = timezone.now()
        self.referendum_not_started.save()
        self.referendum_not_started.refresh_from_db()
        self.assertGreaterEqual(timezone.now(), self.referendum_not_started.event_start)
        self.assertTrue(self.referendum_not_started.is_in_progress)
        response = self.client.get(self.referendum_not_started.get_absolute_url())
        self.assertEqual(nb_vote_token + 1, VoteToken.objects.count())
        last_token = VoteToken.objects.last()
        self.assertEqual(last_token.user, self.citizen)
        self.assertEqual(last_token.referendum, self.referendum_not_started)
        self.vote_token = VoteToken.objects.get(referendum=self.referendum_not_started, user=self.citizen)
        self.assertRedirects(response, reverse('vote', kwargs={'token': self.vote_token.token}))


class ReferendumCreateViewTestCase(TestCase):
    """
    Test CreateReferendumView.
    """

    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.first()

    def test_referendum_creation(self):
        """
        Test a referendum creation.
        """
        data = {
            "title": "referendum test",
            "description": "ceci est un test.",
            "question": "Est-ce vraiment un test ?",
            "categories": [1, 2]
        }
        self.client.force_login(self.user)
        response = self.client.post(reverse('referendum_create'), data=data)
        self.assertRedirects(response, reverse('index'))

    def test_referendum_creation_with_errors(self):
        """
        Test a referendum creation with errors.
        """
        data = {
            "description": "ceci est un test.",
            "question": "Est-ce vraiment un test ?",
            "categories": [1, 2]
        }
        self.client.force_login(self.user)
        response = self.client.post(reverse('referendum_create'), data=data)

        self.assertEqual(response.context_data['form'].fields['title'].error_messages['required'],
                         'Ce champ est obligatoire.')


class ReferendumUpdateViewTestCase(TestCase):
    """
    Test referendum update view.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.permission = Permission.objects.get(codename='is_citizen')
        self.citizen = get_user_model().objects.filter(
            Q(user_permissions=self.permission)).first()
        self.unauthorized_user = get_user_model().objects.exclude(pk=self.citizen.pk).first()
        self.data = [
            {
                "title": "referendum test",
                "description": "ceci est un test.",
                "question": "Est-ce vraiment un test ?",
                "creator_id": self.citizen.pk
            },
            {
                "title": "referendum test publié",
                "description": "ceci est un test 2.",
                "question": "Est-ce vraiment un test 2 ?",
                "creator_id": self.citizen.pk,
                "publication_date": timezone.now()
            },
            {
                "title": "referendum test commencé",
                "description": "ceci est un test 3.",
                "question": "Est-ce vraiment un test 3 ?",
                "creator_id": self.citizen.pk,
                "publication_date": timezone.now(),
                "event_start": timezone.now()
            },
        ]
        self.client = Client()
        self.not_published_referendum = Referendum.objects.create(**self.data[0])
        self.published_referendum = Referendum.objects.create(**self.data[1])
        self.started_referendum = Referendum.objects.create(**self.data[2])

    def test_generated_form_with_not_published_referendum(self):
        """
        Test referendum update view and form when referendum is not published.
        """
        self.client.force_login(self.not_published_referendum.creator)
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.not_published_referendum.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context_data['form'].fields)

    def test_generated_form_with_published_referendum(self):
        """
        Test referendum update view and form when referendum is published.
        """
        self.client.force_login(self.published_referendum.creator)
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.published_referendum.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('title', response.context_data['form'].fields)
        self.assertIn('event_start', response.context_data['form'].fields)

    def test_generated_form_with_started_referendum(self):
        """
        Test referendum update view and form when referendum is published.
        """
        self.client.force_login(self.started_referendum.creator)
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.started_referendum.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('title', response.context_data['form'].fields)
        self.assertNotIn('event_start', response.context_data['form'].fields)

    def test_raise_permission_denied_when_unauthorized_user(self):
        """
        Test that it raises a permission denied error when unauthorized user tries to access update view.
        """
        self.client.force_login(self.unauthorized_user)
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.not_published_referendum.slug}))
        self.assertEqual(response.status_code, 403)

    def test_update_not_published_referendum(self):
        """
        Test referendum update when referendum is not published.
        """
        self.client.force_login(self.not_published_referendum.creator)
        new_data = {**self.data[0], **{'publication_date': timezone.now().strftime("%d/%m/%Y"),
                                       'event_start': '',
                                       'categories': ['1', ]}}
        response = self.client.post(
            reverse('referendum_update', kwargs={'slug': self.not_published_referendum.slug}),
            data=new_data
        )
        self.not_published_referendum.refresh_from_db()
        self.assertRedirects(response, self.not_published_referendum.get_absolute_url())
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.not_published_referendum.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('title', response.context_data['form'].fields)
        self.assertIn('event_start', response.context_data['form'].fields)

    def test_update_published_referendum(self):
        """
        Test referendum update when referendum is published.
        """

        self.client.force_login(self.published_referendum.creator)
        new_data = {'event_start': timezone.now().strftime("%d/%m/%Y")}
        response = self.client.post(
            reverse('referendum_update', kwargs={'slug': self.published_referendum.slug}),
            data=new_data
        )
        self.published_referendum.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('referendum_update', kwargs={'slug': self.published_referendum.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('title', response.context_data['form'].fields)
        self.assertNotIn('event_start', response.context_data['form'].fields)

    def test_update_started_referendum(self):
        """
        Test referendum update when referendum is started.
        """

        self.client.force_login(self.started_referendum.creator)
        old_event_start = self.started_referendum.event_start
        new_data = {'event_start': '31/12/2500'}
        response = self.client.post(
            reverse('referendum_update', kwargs={'slug': self.started_referendum.slug}),
            data=new_data
        )
        self.started_referendum.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.started_referendum.event_start, old_event_start)

    def test_raise_permission_denied_when_unauthorized_user_try_update(self):
        """
        Test that it raises a permission denied error when unauthorized user tries to access update view.
        """
        self.client.force_login(self.unauthorized_user)
        new_data = {**self.data[0], **{'publication_date': timezone.now().strftime("%d/%m/%Y"),
                                       'event_start': '',
                                       'categories': ['1', ]}}
        response = self.client.post(
            reverse('referendum_update', kwargs={'slug': self.not_published_referendum.slug}),
            data=new_data
        )
        self.assertEqual(response.status_code, 403)


class ReferendumVoteViewTestCase(TestCase):
    """
    Test referendum vote view.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.permission = Permission.objects.get(codename='is_citizen')
        self.citizen = get_user_model().objects.filter(
            Q(user_permissions=self.permission)).first()
        self.referendum = Referendum.objects.filter(publication_date__lte=timezone.now(),
                                                    event_start__isnull=True).first()

    def test_unauthenticated_vote(self):
        """
        Test that anonymous user is redirect to login.
        """
        old_nb_votes = self.referendum.nb_votes
        data = {'choice': self.referendum.choice_set.first().pk}
        vote_token = VoteToken.objects.create(user=self.citizen, referendum=self.referendum)
        response = self.client.post(reverse('vote', kwargs={'token': vote_token.token}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(old_nb_votes, self.referendum.nb_votes)

    def test_authenticated_vote_valid_data(self):
        """
        Test that anonymous user get a HttpResponseForbidden.
        """
        self.client.force_login(self.citizen)
        old_nb_votes = self.referendum.nb_votes
        data = {'choice': self.referendum.choice_set.first().pk}
        vote_token = VoteToken.objects.create(user=self.citizen, referendum=self.referendum)
        response = self.client.post(reverse('vote', kwargs={'token': vote_token.token}), data=data)
        self.assertEqual(response.status_code, 302)
        self.referendum.refresh_from_db()
        self.assertEqual(old_nb_votes + 1, self.referendum.nb_votes)
        vote_token.refresh_from_db()
        self.assertTrue(vote_token.voted)

    def test_authenticated_vote_invalid_form(self):
        """
        Test that anonymous user get a HttpResponseForbidden.
        """
        self.client.force_login(self.citizen)
        old_nb_votes = self.referendum.nb_votes
        data = {'choice': "youpi"}
        vote_token = VoteToken.objects.create(user=self.citizen, referendum=self.referendum)
        response = self.client.post(reverse('vote', kwargs={'token': vote_token.token}), data=data)
        self.assertEqual(response.status_code, 200)
        self.referendum.refresh_from_db()
        self.assertEqual(old_nb_votes, self.referendum.nb_votes)
        vote_token.refresh_from_db()
        self.assertFalse(vote_token.voted)
