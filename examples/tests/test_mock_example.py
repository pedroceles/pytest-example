

class DummyDependency(DependencyInjectionService):
    def get_latest_corp(self) -> Corporation:
        return Corporation(id=self.scoped_ids[0], legal_name='Bla')

    @property
    def latest_corp_id(self) -> int:
        return 7


class TestGetCorpName:

    @pytest.fixture
    def dependency_injection_service(self):
        return DependencyInjectionService([1, 2, 3, 4])

    @pytest.fixture
    def mock_patch_get_latest_corp(self, mocker):
        return mocker.patch(
            'eshares.implementations.services.launch.demo_test.DependencyInjectionService.get_latest_corp',
            # autospec=True,
            return_value=Corporation(id=999, legal_name='999 Corp')
        )

    @pytest.fixture
    def mock_patch_object_get_latest_corp(self, mocker, dependency_injection_service):
        return mocker.patch.object(
            dependency_injection_service,
            'get_latest_corp',
            autospec=True,
            return_value=Corporation(id=99, legal_name='99 problems')
        )

    def test_with_dummy_service(self):
        dummy = DummyDependency([1, 2, 3])
        service = ServiceBeingTested(dependency=dummy)
        assert service.get_corp_name() == 'Bla'

    def test_with_mock_patch(self, mock_patch_get_latest_corp):
        service = ServiceBeingTested()
        assert service.get_corp_name() == '999 Corp'

    def test_with_mock_patch_object(self, dependency_injection_service, mock_patch_object_get_latest_corp):
        service = ServiceBeingTested(dependency=dependency_injection_service)
        assert service.get_corp_name() == '99 problems'


class TestGetCorpId:
    @pytest.fixture
    def dependency_injection_service(self):
        return DependencyInjectionService([1, 2, 3, 4])

    @pytest.fixture
    def mock_patch_latest_corp_id(self, mocker):
        return mocker.patch(
            'eshares.implementations.services.launch.demo_test.DependencyInjectionService.latest_corp_id',
            new_callable=mocker.PropertyMock,
            return_value=123
        )

    @pytest.fixture
    def mock_patch_object_latest_corp_id(self, mocker, dependency_injection_service):
        return mocker.patch.object(
            dependency_injection_service,
            'latest_corp_id',
            return_value=321,
            new_callable=mocker.PropertyMock,
        )

    @pytest.fixture
    def mock_printer(self, mocker):
        return mocker.patch(
            'eshares.implementations.services.launch.demo_test.DependencyInjectionService.printer',
            spec=DependencyInjectionService.printer
        )

    def test_with_dummy_service(self):
        dummy = DummyDependency([1, 2, 3])
        service = ServiceBeingTested(dependency=dummy)
        assert service.get_corp_id() == 7

    def test_with_mock_patch(self, mock_patch_latest_corp_id):
        service = ServiceBeingTested()
        assert service.get_corp_id() == 123

    def test_with_mock_patch_object(self, dependency_injection_service, mock_patch_object_latest_corp_id):
        service = ServiceBeingTested(dependency=dependency_injection_service)
        assert service.get_corp_id() == 321

    def test_printer_was_called(self, mock_printer, mock_patch_object_latest_corp_id):
        service = ServiceBeingTested()
        service.get_corp_id()
        mock_printer.assert_called_once_with()
