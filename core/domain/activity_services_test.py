# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from core.domain import activity_domain
from core.domain import activity_services
from core.domain import collection_services
from core.domain import exp_services
from core.domain import rights_manager
from core.tests import test_utils
import feconf


class ActivityServicesTests(test_utils.GenericTestBase):
    """Test the activity services module."""

    EXP_ID_0 = 'EXP_ID_0'
    EXP_ID_1 = 'EXP_ID_1'
    COL_ID_2 = 'COL_ID_2'

    def _get_exploration_reference(self, exploration_id):
        return activity_domain.ActivityReference(
            feconf.ACTIVITY_TYPE_EXPLORATION, exploration_id)

    def _get_collection_reference(self, collection_id):
        return activity_domain.ActivityReference(
            feconf.ACTIVITY_TYPE_COLLECTION, collection_id)

    def _compare_lists(self, reference_list_1, reference_list_2):
        hashes_1 = [reference.get_hash() for reference in reference_list_1]
        hashes_2 = [reference.get_hash() for reference in reference_list_2]
        self.assertEqual(hashes_1, hashes_2)

    def setUp(self):
        """Publish two explorations and one collection."""
        super(ActivityServicesTests, self).setUp()

        self.signup(self.OWNER_EMAIL, self.OWNER_USERNAME)
        self.owner_id = self.get_user_id_from_email(self.OWNER_EMAIL)
        self.signup(self.MODERATOR_EMAIL, self.MODERATOR_USERNAME)
        self.moderator_id = self.get_user_id_from_email(self.MODERATOR_EMAIL)
        self.set_moderators([self.MODERATOR_USERNAME])

        self.save_new_valid_exploration(self.EXP_ID_0, self.owner_id)
        self.save_new_valid_exploration(self.EXP_ID_1, self.owner_id)
        self.save_new_valid_collection(
            self.COL_ID_2, self.owner_id, exploration_id=self.EXP_ID_0)

    def test_basic_operations(self):
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_0)
        rights_manager.publish_collection(self.owner_id, self.COL_ID_2)

        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

        activity_services.update_featured_activity_references([
            self._get_exploration_reference(self.EXP_ID_0),
            self._get_collection_reference(self.COL_ID_2)])
        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_collection_reference(self.COL_ID_2)])

        activity_services.update_featured_activity_references([])
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

    def test_error_handling(self):
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_0)
        rights_manager.publish_collection(self.owner_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

        with self.assertRaisesRegexp(Exception, 'should not have duplicates'):
            activity_services.update_featured_activity_references([
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_exploration_reference(self.EXP_ID_0)])

    def test_deleted_activity_is_removed_from_featured_list(self):
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_0)
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_1)
        rights_manager.publish_collection(self.owner_id, self.COL_ID_2)
        activity_services.update_featured_activity_references([
            self._get_exploration_reference(self.EXP_ID_0),
            self._get_collection_reference(self.COL_ID_2)])

        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_collection_reference(self.COL_ID_2)])

        # Deleting an unfeatured activity does not affect the featured list.
        exp_services.delete_exploration(self.owner_id, self.EXP_ID_1)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_collection_reference(self.COL_ID_2)])

        # Deleting a featured activity removes it from the featured list.
        collection_services.delete_collection(self.owner_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0)])
        exp_services.delete_exploration(self.owner_id, self.EXP_ID_0)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

    def test_unpublished_activity_is_removed_from_featured_list(self):
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_0)
        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_1)
        rights_manager.publish_collection(self.owner_id, self.COL_ID_2)
        activity_services.update_featured_activity_references([
            self._get_exploration_reference(self.EXP_ID_0),
            self._get_collection_reference(self.COL_ID_2)])

        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_collection_reference(self.COL_ID_2)])

        # Unpublishing an unfeatured activity does not affect the featured
        # list.
        rights_manager.unpublish_exploration(self.moderator_id, self.EXP_ID_1)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0),
                self._get_collection_reference(self.COL_ID_2)])

        # Unpublishing a featured activity removes it from the featured list.
        rights_manager.unpublish_collection(self.moderator_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [
                self._get_exploration_reference(self.EXP_ID_0)])

        rights_manager.unpublish_exploration(self.moderator_id, self.EXP_ID_0)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

    def test_publish_or_publicize_activity_does_not_affect_featured_list(self):
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

        rights_manager.publish_exploration(self.owner_id, self.EXP_ID_0)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])
        rights_manager.publicize_exploration(self.moderator_id, self.EXP_ID_0)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])
        rights_manager.unpublicize_exploration(
            self.moderator_id, self.EXP_ID_0)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

        rights_manager.publish_collection(self.owner_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])
        rights_manager.publicize_collection(self.moderator_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])
        rights_manager.unpublicize_collection(
            self.moderator_id, self.COL_ID_2)
        self._compare_lists(
            activity_services.get_featured_activity_references(), [])

    def test_split_by_type(self):
        self.assertEqual(
            activity_services.split_by_type([]), ([], []))

        exploration_123 = self._get_exploration_reference('123')
        self.assertEqual(
            activity_services.split_by_type([exploration_123]),
            (['123'], []))

        collection_def = self._get_collection_reference('def')
        self.assertEqual(
            activity_services.split_by_type([collection_def]),
            ([], ['def']))

        exploration_ab = self._get_exploration_reference('ab')
        self.assertEqual(
            activity_services.split_by_type([
                exploration_123, collection_def, exploration_ab]),
            (['123', 'ab'], ['def']))

        with self.assertRaisesRegexp(Exception, 'Invalid activity reference'):
            activity_services.split_by_type([
                exploration_123,
                activity_domain.ActivityReference('invalid_type', 'bbb')
            ])
