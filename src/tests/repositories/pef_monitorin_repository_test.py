import unittest
from repositories.pef_monitorin_repository import pef_monitoring_repository
from entities.pef_monitoring import PefMonitoring


class TestPefMonitoringRepository(unittest.TestCase):
    def setUp(self):
        pef_monitoring_repository.delete_all_monitoring()

        self.monitoring_entry = PefMonitoring(
            username='Eva',
            date='2025-04-13',
            value1=400,
            value2=410,
            value3=420,
            state='ENNNEN LÄÄKETÄ',
            time='AAMU'
        )

    def test_add_value(self):
        pef_monitoring_repository.add_value(self.monitoring_entry)
        results = pef_monitoring_repository.find_monitoring_by_username('Eva')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], 'Eva')  # username
        self.assertEqual(results[0][2], '2025-04-13')  # date
        self.assertEqual(results[0][3], 400)  # value1

    def test_order_by_date(self):
        second_entry = PefMonitoring(
            username='Eva',
            date='2025-04-12',
            value1=300,
            value2=310,
            value3=320,
            state='LÄÄKKEEN JÄLKEEN',
            time='ILTA'
        )

        pef_monitoring_repository.add_value(self.monitoring_entry)
        pef_monitoring_repository.add_value(second_entry)

        results = pef_monitoring_repository.find_monitoring_by_username('Eva')
        ordered = pef_monitoring_repository.order_by_date(results)

        self.assertEqual(ordered[0][2], '2025-04-12')  # Oldest date first
        self.assertEqual(ordered[1][2], '2025-04-13')

    def test_delete_all_monitoring(self):
        pef_monitoring_repository.add_value(self.monitoring_entry)
        pef_monitoring_repository.delete_all_monitoring()
        results = pef_monitoring_repository.find_monitoring_by_username('Eva')

        self.assertEqual(results, [])
