import pytest
from django.shortcuts import reverse
from django.test import TestCase

from dino.synczones.models import Zone


@pytest.mark.django_db()
def test_zonelistview(client_admin, mock_pdns_get_zones):
    response = client_admin.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' in content
    assert 'example.org.' in content
    assert 'example11.org' in content
    assert 'example400.org' not in content


@pytest.mark.django_db()
def test_zonelistview_sync(client_admin, mock_pdns_get_zones):
    assert Zone.objects.all().count() == 0
    client_admin.get(reverse('zoneeditor:zone_list'))
    assert Zone.objects.all().count() > 2
    assert Zone.objects.filter(name='example.com.').exists()


@pytest.mark.django_db()
def test_zonelistview_filter(client_admin, mock_pdns_get_zones):
    response = client_admin.get(reverse('zoneeditor:zone_list') + '?q=xample.org.')
    response.content.decode()
    assert response.status_code == 200
    assert len(response.context['object_list']) == 1
    assert response.context['object_list'][0].name == 'example.org.'


@pytest.mark.parametrize('q', [
    'example.org',
    'example.org.',
])
@pytest.mark.django_db()
def test_zonelistview_jump(client_admin, mock_pdns_get_zones, q):
    response = client_admin.get(reverse('zoneeditor:zone_list') + f'?q={q}')
    TestCase().assertRedirects(response, f'/zones/example.org.', fetch_redirect_response=False)


@pytest.mark.django_db()
def test_zonelistview_unauthenicated(client):
    url = reverse('zoneeditor:zone_list')
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}', fetch_redirect_response=False)


@pytest.mark.django_db()
def test_zonelistview_user_tenant_admin(client_user_tenant_admin, mock_pdns_get_zones):
    response = client_user_tenant_admin.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' in content
    assert 'example.org.' not in content
    assert 'example16.org' not in content


@pytest.mark.django_db()
def test_zonelistview_user_no_tenant(client_user_no_tenant, mock_pdns_get_zones):
    response = client_user_no_tenant.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' not in content
    assert 'example.org.' not in content
    assert 'example16.org' not in content
