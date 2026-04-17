from django.contrib.auth import get_user_model # type: ignore from django.contrib.auth
from django.test import TestCase # type: ignore from django.test

from churches.models import Church, Subscription, SubscriptionPlan
from common.tenant import filter_queryset_for_tenant, user_has_active_subscription
from hierarchy.models import National, Region
from members.models import Fidele

User = get_user_model()


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.ch_a = Church.objects.create(name='Église A', email='a@test.org', phone='')
        self.ch_b = Church.objects.create(name='Église B', email='b@test.org', phone='')
        Subscription.objects.create(
            church=self.ch_a, plan=SubscriptionPlan.FREE, is_active=True
        )
        Subscription.objects.create(
            church=self.ch_b, plan=SubscriptionPlan.FREE, is_active=True
        )
        self.nat_a = National.objects.create(
            church=self.ch_a, nom='Nat A', pays='SN', email='a@test.org', telephone=''
        )
        self.nat_b = National.objects.create(
            church=self.ch_b, nom='Nat B', pays='SN', email='b@test.org', telephone=''
        )
        Region.objects.create(church=self.ch_a, national=self.nat_a, code='AA', nom='Région A')
        Region.objects.create(church=self.ch_b, national=self.nat_b, code='AA', nom='Région B')
        self.user_a = User.objects.create_user(
            email='usera@test.org',
            password='pass12345!!',
            first_name='U',
            last_name='A',
            church=self.ch_a,
            role='admin_national',
        )

    def test_filter_regions_by_tenant(self):
        qs = Region.objects.all()
        scoped = filter_queryset_for_tenant(qs, self.user_a)
        self.assertEqual(scoped.count(), 1)
        self.assertEqual(scoped.first().church_id, self.ch_a.id)

    def test_active_subscription(self):
        self.assertTrue(user_has_active_subscription(self.user_a))

    def test_superadmin_no_church_sees_all_regions(self):
        superu = User.objects.create_user(
            email='super@test.org',
            password='pass12345!!',
            first_name='S',
            last_name='U',
            role='super_admin',
            is_staff=True,
            is_superuser=True,
        )
        qs = filter_queryset_for_tenant(Region.objects.all(), superu)
        self.assertGreaterEqual(qs.count(), 2)
