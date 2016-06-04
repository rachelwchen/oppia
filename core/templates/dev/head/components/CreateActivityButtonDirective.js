// Copyright 2016 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Directive for the Create Exploration/Collection button.
 */

oppia.directive('createActivityButton', [function() {
  return {
    restrict: 'E',
    templateUrl: 'components/createActivityButton',
    controller: [
      '$scope', '$timeout', '$window', '$modal', 'ExplorationCreationService',
      'CollectionCreationService', 'siteAnalyticsService', 'urlService',
      function(
          $scope, $timeout, $window, $modal, ExplorationCreationService,
          CollectionCreationService, siteAnalyticsService, urlService) {
        $scope.creationInProgress = false;

        $scope.showUploadExplorationModal = (
          ExplorationCreationService.showUploadExplorationModal);

        $scope.onRedirectToLogin = function(destinationUrl) {
          siteAnalyticsService.registerStartLoginEvent('createActivityButton');
          $timeout(function() {
            $window.location = destinationUrl;
          }, 150);
          return false;
        };

        $scope.showCreationChoiceModal = function() {
          $scope.creationInProgress = true;
          if (urlService.getPathname() !== '/dashboard') {
            $window.location.replace('/dashboard?mode=create');
          } else {
            $modal.open({
              templateUrl: 'modals/createActivity',
              backdrop: true,
              controller: [
                  '$scope', '$modalInstance', function($scope, $modalInstance) {
                $scope.chooseExploration = function() {
                  ExplorationCreationService.createNewExploration();
                  $modalInstance.close();
                };

                $scope.chooseCollection = function() {
                  CollectionCreationService.createNewCollection();
                  $modalInstance.close();
                };

                $scope.cancel = function() {
                  $modalInstance.dismiss('cancel');
                };
              }],
              windowClass: 'oppia-creation-modal'
            }).result.then(function() {}, function() {
              $scope.creationInProgress = false;
            });
          }
        };

        // If the user clicked on a 'create' button to get to the dashboard,
        // open the create modal immediately.
        if (urlService.getUrlParams().mode === 'create') {
          $scope.showCreationChoiceModal();
        }
      }
    ]
  };
}]);
