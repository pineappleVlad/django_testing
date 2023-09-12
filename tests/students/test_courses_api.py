import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_course_retrieve(client, course_factory):

    courses = course_factory(_quantity=1)
    id = courses[0].id

    url = reverse('courses-detail', kwargs={'pk': id})
    response = client.get(url)

    db_course = Course.objects.get(pk=id)

    assert response.status_code == 200
    assert response.data.get('name') == db_course.name


@pytest.mark.django_db #all_courses
def test_course_list(client, course_factory):
    courses = course_factory(_quantity=5)

    response = client.get('/api/v1/courses/')
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 5


@pytest.mark.django_db
def test_id_course_filter(client, course_factory):
    courses = course_factory(_quantity=5)
    id = courses[0].id

    url = reverse('courses-list')
    url_filter = url + f'?id={id}'

    response = client.get(url_filter)
    db_course = Course.objects.get(pk=id)

    assert response.status_code == 200
    assert response.data[0]['name'] == db_course.name


@pytest.mark.django_db
def test_name_course_filter(client, course_factory):
    courses = course_factory(_quantity=5)
    name = courses[0].name

    url = reverse('courses-list')
    url_filter = url + f'?name={name}'

    response = client.get(url_filter)
    db_course = Course.objects.get(name=name)

    assert response.status_code == 200
    assert response.data[0]['id'] == db_course.id


@pytest.mark.django_db
def test_course_create(client):
    count = Course.objects.count()

    response = client.post('/api/v1/courses/', data={'name': 'Ivan'})
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_course_update(client, course_factory):
    course = course_factory(_quantity=5)
    id = course[0].id
    url = reverse('courses-detail', kwargs={'pk': id})
    data = {'name': 'Ivan'}
    response = client.put(url, data)
    db_course = Course.objects.get(pk=id)

    assert response.status_code == 200
    assert db_course.name == data['name']


@pytest.mark.django_db
def test_course_delete(client, course_factory):
    courses = course_factory(_quantity=5)
    count = Course.objects.count()

    id = courses[0].id
    url = reverse('courses-detail', kwargs={'pk': id})
    response = client.delete(url)

    assert response.status_code == 204
    assert Course.objects.count() == count - 1

