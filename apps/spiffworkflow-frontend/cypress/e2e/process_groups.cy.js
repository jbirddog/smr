describe('process-groups', () => {
  beforeEach(() => {
    cy.login();
  });
  afterEach(() => {
    cy.logout();
  });

  it('can perform crud operations', () => {
    const uuid = () => Cypress._.random(0, 1e6);
    const id = uuid();
    const groupDisplayName = `Test Group 1 ${id}`;
    const newGroupDisplayName = `${groupDisplayName} edited`;
    const groupId = `test-group-1-${id}`;
    cy.createGroup(groupId, groupDisplayName);

    cy.contains('Process Groups').click();
    cy.contains(groupId);
    cy.contains(groupId).click();
    cy.url().should('include', `process-groups/${groupId}`);
    cy.contains(`Process Group: ${groupId}`);

    cy.contains('Edit process group').click();
    cy.get('input[name=display_name]').clear().type(newGroupDisplayName);
    cy.contains('Submit').click();
    cy.contains(`Process Group: ${groupId}`);

    cy.contains('Edit process group').click();
    cy.get('input[name=display_name]').should(
      'have.value',
      newGroupDisplayName
    );

    cy.contains('Delete').click();
    cy.contains('Are you sure');
    cy.contains('OK').click();
    cy.url().should('include', `process-groups`);
    cy.contains(groupId).should('not.exist');
  });

  it('can paginate items', () => {
    cy.basicPaginationTest();
  });
});
