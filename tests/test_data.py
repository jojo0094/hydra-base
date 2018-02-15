# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hydra_base as hb
from hydra_base.lib.objects import JSONObject, Dataset
import server
from fixtures import *
import pytest
import util
import datetime
import logging
from suds import WebFault
import json
log = logging.getLogger(__name__)


@pytest.fixture()
def relative_timeseries():
    """
        Create a timeseries which has relative timesteps:
        1, 2, 3 as opposed to timestamps
    """
    t1 = "1.0"
    t2 = "2.0"
    t3 = "3.0"
    val_1 = [[[1, 2, "hello"], [5, 4, 6]], [[10, 20, 30], [40, 50, 60]], [[9, 8, 7], [6, 5, 4]]]
    val_2 = ["1.0", "2.0", "3.0"]
    val_3 = ["3.0", "", ""]

    timeseries = json.dumps({0: {t1: val_1, t2: val_2, t3: val_3}})

    return timeseries


@pytest.fixture()
def arbitrary_timeseries():
    """
        Create a timeseries which has relative timesteps:
        1, 2, 3 as opposed to timestamps
    """
    t1 = 'arb'
    t2 = 'it'
    t3 = 'rary'
    val_1 = [[[1, 2, "hello"], [5, 4, 6]], [[10, 20, 30], [40, 50, 60]], [[9,8,7],[6,5,4]]]
    val_2 = ["1.0", "2.0", "3.0"]
    val_3 = ["3.0", "", ""]

    timeseries = json.dumps({0:{t1:val_1, t2:val_2, t3:val_3}})

    return timeseries


@pytest.fixture()
def seasonal_timeseries():
    """
        Create a timeseries which has relative timesteps:
        1, 2, 3 as opposed to timestamps
    """
    t1 ='9999-01-01'
    t2 ='9999-02-01'
    t3 ='9999-03-01'
    val_1 = [[[1, 2, "hello"], [5, 4, 6]], [[10, 20, 30], [40, 50, 60]], [[9,8,7],[6,5,4]]]

    val_2 = ["1.0", "2.0", "3.0"]
    val_3 = ["3.0", "", ""]

    timeseries = json.dumps({0: {t1: val_1, t2: val_2, t3: val_3}})

    return timeseries


class TestTimeSeries:
    """
        Test for timeseries-based functionality
    """
    # Todo make this a fixture?
    user_id = util.user_id

    @pytest.mark.xfail(reason='Relative timesteps are being converted to timestamps. ')
    def test_relative_timeseries(self, session, network, relative_timeseries):
        """
            Test for relative timeseries for example, x number of hours from hour 0.
        """
        s = network['scenarios'][0]
        assert len(s['resourcescenarios']) > 0
        for rs in s['resourcescenarios']:
            if rs['value']['type'] == 'timeseries':
                rs['value']['value'] = relative_timeseries

        new_network_summary = hb.add_network(network, user_id=self.user_id)
        new_net = hb.get_network(new_network_summary.id, user_id=self.user_id, include_data='Y')

        new_s = new_net['scenarios'][0]
        new_rss = new_s['resourcescenarios']

        assert len(new_rss) > 0
        for new_rs in new_rss:
            if new_rs.value.type == 'timeseries':
                ret_ts_dict = json.loads(new_rs.value.value).values()[0]
                client_ts   = json.loads(relative_timeseries)['0']
                for new_timestep in client_ts.keys():
                    # TODO this bit appears broken. Somewhere in hydra the timesteps
                    # are convert to timestamps.
                    assert ret_ts_dict.get(new_timestep) == client_ts[new_timestep]


    def test_arbitrary_timeseries(self, session, network, arbitrary_timeseries):

        s = network['scenarios'][0]
        for rs in s['resourcescenarios']:
            if rs['value']['type'] == 'timeseries':
                rs['value']['value'] = arbitrary_timeseries

        new_network_summary = hb.add_network(network, user_id=self.user_id)
        new_net = hb.get_network(new_network_summary.id, user_id=self.user_id)

        new_s = new_net.scenarios[0]
        new_rss = new_s.resourcescenarios
        for new_rs in new_rss:
            if new_rs.value.type == 'timeseries':
                ret_ts_dict = {}
                ret_ts_dict = json.loads(new_rs.value.value).values()[0]
                client_ts   = json.loads(arbitrary_timeseries)['0']
                for new_timestep in client_ts.keys():
                    assert ret_ts_dict[new_timestep] == client_ts[new_timestep]

    @pytest.mark.xfail(reason='Not sure why this is not working. Needs more investigation.')
    def test_get_relative_data_between_times(self, session, network, relative_timeseries):

        # TODO The following is shared with `test_relative_timeseries` it could be put in a fixture
        s = network['scenarios'][0]
        assert len(s['resourcescenarios']) > 0
        for rs in s['resourcescenarios']:
            if rs['value']['type'] == 'timeseries':
                rs['value']['value'] = relative_timeseries

        new_network_summary = hb.add_network(network, user_id=self.user_id)
        new_net = hb.get_network(new_network_summary.id, user_id=self.user_id, include_data='Y')

        scenario = new_net.scenarios[0]
        val_to_query = None
        for d in scenario.resourcescenarios:
            if d.value.type == 'timeseries':
                val_to_query = d.value
                break

        now = datetime.datetime.now()

        x = hb.get_vals_between_times(
            val_to_query.id,
            0,
            5,
            None,
            0.5,
            )
        assert len(x.data) > 0

        invalid_qry = hb.get_vals_between_times(
            val_to_query.id,
            now,
            now + datetime.timedelta(minutes=75),
            'minutes',
            )

        assert eval(invalid_qry.data) == []

    def test_seasonal_timeseries(self, session, network, seasonal_timeseries):

        s = network['scenarios'][0]
        for rs in s['resourcescenarios']:
            if rs['value']['type'] == 'timeseries':
                rs['value']['value'] = seasonal_timeseries

        new_network_summary = hb.add_network(network, user_id=self.user_id)
        new_net = hb.get_network(new_network_summary.id, user_id=self.user_id, include_data='Y')

        scenario = new_net.scenarios[0]
        val_to_query = None
        for d in scenario.resourcescenarios:
            if d.value.type == 'timeseries':
                val_to_query = d.value
                break

        val_a = json.loads(val_to_query.value).values()[0]

        jan_val = hb.get_val_at_time(
            val_to_query.id,
            [datetime.datetime(2000, 1, 10, 00, 00, 00), ]
           )
        feb_val = hb.get_val_at_time(
            val_to_query.id,
            [datetime.datetime(2000, 2, 10, 00, 00, 00), ]
           )
        mar_val = hb.get_val_at_time(
            val_to_query.id,
            [datetime.datetime(2000, 3, 10, 00, 00, 00), ]
           )
        oct_val = hb.get_val_at_time(
            val_to_query.id,
            [datetime.datetime(2000, 10, 10, 00, 00, 00), ]
           )

        local_val = json.loads(val_to_query.value).values()[0]
        assert json.loads(jan_val.data) == local_val['9999-01-01']
        assert json.loads(feb_val.data) == local_val['9999-02-01']
        assert json.loads(mar_val.data) == local_val['9999-03-01']
        assert json.loads(oct_val.data) == local_val['9999-03-01']

        start_time = datetime.datetime(2000, 7, 10, 00, 00, 00)
        vals = hb.get_vals_between_times(
            val_to_query.id,
            start_time,
            start_time + datetime.timedelta(minutes=75),
            'minutes',
            1,
            )

        data = json.loads(vals.data)
        original_val = local_val['9999-03-01']
        assert len(data) == 76
        for val in data:
            assert original_val == val

    def test_multiple_vals_at_time(self, session, network_with_data, seasonal_timeseries):

        # Convenience renaming
        network = network_with_data

        s = network['scenarios'][0]
        for rs in s['resourcescenarios']:
            if rs['value']['type'] == 'timeseries':
                rs['value']['value'] = seasonal_timeseries

        new_network_summary = hb.add_network(network)
        new_net = hb.get_network(new_network_summary.id)

        scenario = new_net.scenarios[0]
        val_to_query = None
        for d in scenario.resourcescenarios:
            if d.value.type == 'timeseries':
                val_to_query = d.value
                break

        val_a = json.loads(val_to_query.value)

        qry_times =             [
            datetime.datetime(2000, 1, 10, 00, 00, 00),
            datetime.datetime(2000, 2, 10, 00, 00, 00),
            datetime.datetime(2000, 3, 10, 00, 00, 00),
            datetime.datetime(2000, 10, 10, 00, 00, 00),
            ]

        seasonal_vals = hb.get_multiple_vals_at_time(
            val_to_query.id,
            qry_times,
           )

        return_val = json.loads(seasonal_vals['dataset_%s'%val_to_query.id])

        dataset_vals = val_a['0.0']

        assert return_val[str(qry_times[0])] == dataset_vals['9999-01-01']
        assert return_val[str(qry_times[1])] == dataset_vals['9999-02-01']
        assert return_val[str(qry_times[2])] == dataset_vals['9999-03-01']
        assert return_val[str(qry_times[3])] == dataset_vals['9999-03-01']

        start_time = datetime.datetime(2000, 7, 10, 00, 00, 00)
        vals = hb.get_vals_between_times(
            val_to_query.id,
            start_time,
            start_time + datetime.timedelta(minutes=75),
            'minutes',
            1,
            )

        data = json.loads(vals.data)
        original_val = dataset_vals['9999-03-01']
        assert len(data) == 76
        for val in data:
            assert original_val == val

    def test_get_data_between_times(self, session, network_with_data):

        # Convenience renaming
        net = network_with_data

        scenario = net.scenarios[0]
        val_to_query = None
        for d in scenario.resourcescenarios:
            if d.value.type == 'timeseries':
                val_to_query = d.value
                break

        val_a = json.loads(val_to_query.value)['index'].values()[0]
        val_b = json.loads(val_to_query.value)['index'].values()[1]

        now = datetime.datetime.now()

        vals = hb.get_vals_between_times(
            val_to_query.id,
            now,
            now + datetime.timedelta(minutes=75),
            'minutes',
            1,
            )

        data = json.loads(vals.data)
        assert len(data) == 76
        for val in data[60:75]:
            x = val_b
            assert x == val_b
        for val in data[0:59]:
            x = val_a
            assert x == val_a

    def test_descriptor_get_data_between_times(self, session, network_with_data):
        net = network_with_data
        scenario = net.scenarios[0]
        val_to_query = None
        for d in scenario.resourcescenarios:
            if d.value.type == 'descriptor':
                val_to_query = d.value
                break

        now = datetime.datetime.now()

        value = hb.get_vals_between_times(
            val_to_query.id,
            now,
            now + datetime.timedelta(minutes=75),
            'minutes',
            )

        assert json.loads(value.data) == ['test']



#Commented out because an imbalanced array is now allowed. We may add checks
#for this at a later date if needed, but for now we are going to leave such
#validation up to the client.
#class ArrayTest(server.HydraBaseTest):
#    def test_array_format(self):
#        bad_net = self.build_network()
#
#        s = bad_net['scenarios'].Scenario[0]
#        for rs in s['resourcescenarios'].ResourceScenario:
#            if rs['value']['type'] == 'array':
#                rs['value']['value'] = json.dumps([[1, 2] ,[3, 4, 5]])
#
#        self.assertRaises(WebFault, hb.add_network,bad_net)
#
#        net = self.build_network()
#        n = hb.add_network(net)
#        good_net = hb.get_network(n.id)
#
#        s = good_net.scenarios.Scenario[0]
#        for rs in s.resourcescenarios.ResourceScenario:
#            if rs.value.type == 'array':
#                rs.value.value = json.dumps([[1, 2] ,[3, 4, 5]])
#                #Get one of the datasets, make it uneven and update it.
#                self.assertRaises(WebFault, hb.update_dataset,rs)

@pytest.fixture
def collection_json_object():
    collection = JSONObject(dict(
        type="descriptor",
        name="Test collection"
    ))
    return collection


@pytest.fixture()
def dataset_json_object():
    ds = Dataset(dict(
        type="array",
        integer=[],
    ))
    return ds


class TestDataCollection:

    def test_get_collections_like_name(self, session):
        collections = hb.get_collections_like_name('test')

        assert len(collections) > 0, "collections were not retrieved correctly!"

    def test_get_collection_datasets(self, session):
        collections = hb.get_collections_like_name('test')

        datasets = hb.get_collection_datasets(collections[-1].id)

        assert len(datasets) > 0, "Datasets were not retrieved correctly!"

    @pytest.mark.xfail(reason='The DatasetCollection has 3 items instead of 2. ')
    def test_add_collection(self, session, network_with_data, dataset_json_object, collection_json_object):

        network = network_with_data

        scenario_id = network.scenarios[0].id

        scenario_data = hb.get_scenario_data(scenario_id)

        collection = collection_json_object

        dataset_id = scenario_data[0].dataset_id
        dataset_json_object.integer.append(dataset_id)
        for d in scenario_data:
            print(d)
            if d.data_type == 'timeseries' and d.dataset_id != dataset_id:
                dataset_json_object.integer.append(d.dataset_id)
                break

        collection.dataset_ids = dataset_json_object
        collection.name  = 'test soap collection %s'%(datetime.datetime.now())

        newly_added_collection = hb.add_dataset_collection(collection)

        assert newly_added_collection.collection_id is not None, "Dataset collection does not have an ID!"
        assert len(newly_added_collection.items) == 2, "Dataset collection does not have any items!"

