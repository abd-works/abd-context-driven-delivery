/**
 * Epic: Browse Books
 * Map: ../../../.context/story-map.md#s-customer----search-books
 * Model: ../../../.context/domain-model.md
 */

import { scenario, story } from "../../story-test";

/**
 * Story: Search Books
 * Actor: Customer
 */
story("Search Books", () => {
  scenario("Find a book by a word of its title", ({ given, when, then }) => {
    given("the Bookshop sells [Book](../../../.context/domain-model.md#book-aggregate-root-entity) Tiny Tales", () => {
      // domain state only
    });
    when("the Customer searches for Tiny", () => {
      // test code goes here
    });
    then("the Customer sees [Book](../../../.context/domain-model.md#book-aggregate-root-entity) Tiny Tales at price 5", () => {
      // test code goes here
    });
  });

  scenario("Find nothing for an unknown word", ({ given, when, then }) => {
    given("the Bookshop sells [Book](../../../.context/domain-model.md#book-aggregate-root-entity) Tiny Tales", () => {
      // domain state only
    });
    when("the Customer searches for Zebra", () => {
      // test code goes here
    });
    then("the Customer sees no [Book](../../../.context/domain-model.md#book-aggregate-root-entity)", () => {
      // test code goes here
    }).and("the Customer sees \"No books match Zebra\"", () => {
      // test code goes here
    });
  });
});
