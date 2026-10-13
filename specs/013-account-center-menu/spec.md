# Feature Specification: Account Center menu entries that appear only for the people they apply to

**Feature Branch**: `013-account-center-menu`

**Created**: 2026-07-31

**Status**: Draft

**Serves**: G3 (a shared management layout), G6 (per-user relevance) · **Roadmap**: R2 · **Issue**: #42

**Input**: User description: "Account Center menu entries appear only for the people they apply to. An integration answers, per request, whether each of its menu entries applies to the person looking at the page right now. An entry that does not apply is absent from the menu, and a section header whose entries are all absent is absent with them. Hiding is presentation only: the URL behind a hidden entry still resolves, and who may open that page remains the integration's own concern. An entry whose integration declares nothing stays visible, exactly as today. Alongside this, confirm that any integration can serve a management view through the shared management page without special-casing, and correct ADR 0002 to cite roadmap item R2 and to read as implemented."

## Clarifications

### Session 2026-07-31

- Q: When someone opens a management page whose menu entry is hidden from them, does the page frame degrade? → A: ~~No. The breadcrumb and the sub menu render as they do for anyone else on that page.~~ **Superseded 2026-07-31:** the requirement is dropped. Resolving a section independently of visibility means this package re-deriving navigation state the menu library already owns, and the maintainer declined to carry that. A person who deep-links to a page whose entry is hidden from them gets no section crumb. Tracked for a template-based redesign; see D9.
- Q: What is this feature's canonical name for an integration's per-request answer? → A: **Visibility check**, matching the word CONTEXT.md and ADR 0002 already use.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - [Developer] An integration says who each menu entry is for (Priority: P1)

A developer is building an integration whose pages apply to some people and not others — billing
for the people on a paid plan, team settings for the people in a team. Today their only lever is
`INSTALLED_APPS`, which is a project-wide answer to a per-person question. Installing the
integration puts its entries in front of everyone signed in, including the people it means
nothing to. After this feature the developer attaches a visibility check to each entry they
contribute, and the Account Center asks it while it is building the menu for whoever is looking.

**Why this priority**: This is the mechanism the whole feature rests on, and the one G6 names.
Nothing else in this spec is reachable without it.

**Independent Test**: Contribute two menu entries from an app outside the core package, one that
answers yes for a given person and one that answers no, then render the Account Center as that
person and assert only the first is present.

**Acceptance Scenarios**:

1. **Given** an integration that contributes a menu entry with a visibility check, **When** the
   Account Center renders for a person the entry applies to, **Then** the entry is present in the
   menu.
2. **Given** the same integration and the same entry, **When** the Account Center renders for a
   person the entry does not apply to, **Then** the entry is absent from the menu.
3. **Given** an entry whose answer depends on the person, **When** two different people load the
   same page, **Then** each is answered for separately rather than one answer being reused.
4. **Given** a menu entry contributed without a visibility check, **When** the Account Center
   renders for any signed-in person, **Then** the entry is present, as it is today.

---

### User Story 2 - [End User] The menu lists only what applies to me (Priority: P1)

Someone signed in opens their Account Center and reads a menu of the things they can actually
manage. They do not see a Billing entry when they are on no plan, or a Team entry when they are
in no team. If a whole section turns out to hold nothing for them, the section's heading is gone
too rather than sitting above empty space.

**Why this priority**: This is what a person experiences, and it is the failure the feature
exists to remove — a menu that lists things you cannot use is worse than a shorter menu.
Implemented alongside US-1, which is the same change seen from the developer's side.

**Independent Test**: Sign in as two people whose integrations apply differently and compare the
rendered menus.

**Acceptance Scenarios**:

1. **Given** two signed-in people and one installed set of integrations, **When** each loads an
   Account Center page, **Then** the menu each reads lists only the entries that apply to them.
2. **Given** a person for whom every entry in one section does not apply, **When** they load an
   Account Center page, **Then** neither the entries nor the section heading appear.
3. **Given** a person for whom an entry does not apply, **When** they load an Account Center
   page, **Then** the rest of the menu and the page content are unaffected.
4. **Given** a person following a link to a page whose menu entry is hidden from them, **When**
   they open it, **Then** the page behaves exactly as it did before this feature, because the
   integration alone decides who may open it.

---

### User Story 3 - [Developer] A second integration serves a page through the shared management page (Priority: P2)

A developer writes a management view in their own integration and wants it to look like every
other Account Center page:

- the Account Center menu in the sidebar
- the breadcrumbs above the content
- its own content in the middle

The shared management page is owned by the core package and is meant to carry exactly this, but
`dac.allauth` is the only integration that has ever served a page through it, so nothing
establishes that a second one can without special handling.

**Why this priority**: G3 promises that a management page written by one integration is
indistinguishable in shape from one written by another, and one integration cannot demonstrate
that. It is P2 rather than P1 because the shared page already exists — this proves and documents
a contract rather than building one.

**Independent Test**: Serve a management view from an app that does not depend on `dac.allauth`
through the shared management page and assert it renders with the Account Center menu, the breadcrumbs and
its own content.

**Acceptance Scenarios**:

1. **Given** an integration other than `dac.allauth`, **When** its management view renders
   through the shared management page, **Then** the page carries the Account Center menu, the breadcrumbs
   and the view's own content.
2. **Given** that integration, **When** it is added to a project, **Then** it reaches the shared
   management page without any change to the core package.
3. **Given** a project with `dac.allauth` absent, **When** another integration's management view
   renders, **Then** it renders correctly and references no template belonging to an integration.

---

### User Story 4 - [Developer] The recorded decision matches the built behaviour (Priority: P3)

A developer reading the package's decision record finds ADR 0002 describing per-request
visibility as accepted and not yet implemented, and pointing at roadmap item R6, which is now the
allauth item. Both statements are wrong once this feature lands, and a decision record that
misdescribes the code is worse than none.

**Why this priority**: Documentation correctness, landing with the change it describes. It cannot
be done before the behaviour exists, and it must not be left behind.

**Independent Test**: Read ADR 0002 and confirm its status, its roadmap reference and its
description of the code match what the package does.

**Acceptance Scenarios**:

1. **Given** ADR 0002 after this feature lands, **When** it is read, **Then** it cites R2 as the
   roadmap item and records the decision as implemented for menu entries.
2. **Given** ADR 0002's account of what the code does, **When** compared against the code,
   **Then** it describes menu entries as resolved per request rather than at import.
3. **Given** the glossary and the integration-facing prose that describe visibility as decided
   but not built, **When** read after this feature lands, **Then** they describe the behaviour
   that exists.

### Edge Cases

- A menu entry contributed with no visibility check stays visible whenever its integration is
  installed. Existing integrations keep working untouched, and answering is something an
  integration opts into.
- The core package's own Overview entry applies to every signed-in person and is never hidden.
- The Account Center is behind a sign-in requirement, so entries are only ever resolved for a
  signed-in person. There is no anonymous case to answer for.
- An integration's answer that raises is not swallowed. A broken answer surfaces as an error
  rather than silently removing an entry, because an entry that vanishes without explanation is
  the harder failure to diagnose.
- Hiding a section's last entry hides the section heading. This is behaviour the menu library
  already provides, and this package relies on it rather than reimplementing or re-testing it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An integration MUST be able to declare, for each menu entry it contributes, whether
  that entry applies to the person making the current request. *(US-1)*
- **FR-002**: The visibility check MUST be evaluated for each request rather than once when the
  process starts, so that two people loading the same page are answered for separately. *(US-1)*
- **FR-003**: A menu entry that does not apply to the current person MUST be absent from the
  rendered menu. *(US-1, US-2)*
- **FR-004**: A section whose entries are all absent for the current person MUST render neither
  its entries nor its heading. *(US-2)*
- **FR-005**: A menu entry contributed without a visibility check MUST remain visible whenever its
  integration is installed, preserving today's behaviour for existing integrations. *(US-1)*
- **FR-006**: Hiding a menu entry MUST NOT change whether the URL behind it resolves, nor what
  the view behind it does. Access to the page remains the contributing integration's
  responsibility. *(US-2)*
- **FR-007**: The entries `dac.allauth` contributes today MUST continue to appear exactly as they
  do now for a person to whom they apply. *(US-2)*
- **FR-008**: An integration other than `dac.allauth` MUST be able to serve a management view
  through the shared management page, carrying the Account Center menu, the breadcrumbs and its own content,
  with no change to the core package. *(US-3)*
- **FR-009**: ADR 0002 MUST cite roadmap item R2, record the decision as implemented for menu
  entries, and describe the code as it then stands. *(US-4)*
- **FR-010**: Package documentation that describes Account Center visibility as decided but not
  built MUST be updated to describe the behaviour that exists. *(US-4)*
- **FR-011**: CONTEXT.md MUST define "visibility check" as the canonical term for an
  integration's per-request answer, so the concept has one name across code, tests and docs.
  *(US-4)*

### Key Entities

- **Visibility check**: The answer an integration gives, for one menu entry and one request, to
  whether that entry applies to the person making the request. This is the feature's canonical
  term. It reuses the word CONTEXT.md and ADR 0002 already use for this concept, and the spec
  uses no synonym for it.
- **Menu entry**: One item in the Account Center menu, contributed by the core package or by an
  integration. It carries:
  - a label
  - an icon
  - a destination
  - after this feature, an optional visibility check
- **Section**: A labelled group of menu entries contributed by one integration, present only
  while it holds at least one entry that applies.
- **Integration**: A gated sub-app that contributes entries, cards and pages to the Account
  Center, and which now also answers who each of its entries is for.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two signed-in people with different circumstances, in one project with one set of
  installed integrations, read Account Center menus that differ in exactly the entries that do
  not apply to them.
- **SC-002**: Every entry an integration contributes can be made to appear for one person and not
  another without any change to the core package.
- **SC-003**: A person is never shown a menu entry leading to a page that has nothing for them,
  and is never shown a section heading with nothing beneath it.
- **SC-004**: An integration written before this feature, contributing entries with no
  visibility check, produces the same menu it produced before.
- **SC-005**: A management view served by an integration other than `dac.allauth` is
  indistinguishable in page shape from one served by `dac.allauth`.
- **SC-006**: A developer reading ADR 0002 and the package's integration-facing documentation
  finds no statement that contradicts the code.

## Assumptions

- Visibility here is presentation only. Whether a person may open a page is decided by the
  integration's own view, and this feature neither adds nor removes any access control. Confirmed
  with the maintainer at intake.
- A visibility check is optional. An integration that says nothing keeps today's behaviour, and
  this is a compatibility guarantee under Article XV rather than a transitional state.
- Hiding a section that has no visible entries is behaviour the underlying menu library already
  provides. This feature depends on it and does not duplicate its tests.
- Overview cards carry the same per-request question and are deliberately out of scope. They are
  roadmap item R3 and have their own feature.
- Contributing an integration's URLs without an edit to the core package is roadmap item R4 and
  is out of scope. US-3 proves the page and menu contract, not zero-wiring reachability.
- The example project and the existing allauth integration are the reference consumers. No
  consuming project outside this repository is assumed to exist.
