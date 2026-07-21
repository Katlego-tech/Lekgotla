Feature: Compile agent configuration
  As a repository maintainer
  I want Lekgotla to resolve contradictory instructions
  So that my agents receive one dependable manifest

  Scenario: Apply a selected package-manager resolution
    Given config sources that disagree on the package manager
    When I compile the sources with "npm" selected
    Then the manifest uses "npm" for package operations
