from django.test import TestCase  # pyright: ignore[reportMissingImports]
from django.contrib.auth import get_user_model  # pyright: ignore[reportMissingImports]
from rest_framework.test import APIClient  # pyright: ignore[reportMissingImports]

from churches.models import Church
from hierarchy.models import National

User = get_user_model()


class RegisterChurchApiTests(TestCase):
    def test_register_creates_church_and_admin(self):
        client = APIClient()
        res = client.post(
            '/api/v1/auth/register/',
            {
                'church_name': 'Nouvelle Église',
                'church_email': 'contact@nouvelle.test',
                'church_phone': '010203',
                'admin_email': 'admin@nouvelle.test',
                'admin_password': 'Motdepasse123!',
                'admin_first_name': 'Jean',
                'admin_last_name': 'Admin',
            },
            format='json',
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertTrue(Church.objects.filter(name='Nouvelle Église').exists())
        ch = Church.objects.get(name='Nouvelle Église')
        self.assertTrue(National.objects.filter(church=ch).exists())
        self.assertTrue(User.objects.filter(email='admin@nouvelle.test', church=ch).exists())
