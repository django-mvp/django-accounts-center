from invoke import task


@task
def prerelease(c, no_test=False):
    """
    Run comprehensive pre-release checks and update all required files.

    This task performs all necessary steps to prepare the repository for release:
    1. Run linting, formatting, type checking, and dependency checks via pre-commit hooks
    2. Run quality checks and tests

    Use this before running the release task to ensure everything is ready.

    Pre-commit hooks include:
    - Code formatting (Ruff)
    - Type checking (mypy)
    - Dependency analysis (deptry)
    - Lockfile validation
    """
    print("🚀 Starting comprehensive pre-release checks...")
    print("=" * 60)

    # Step 1: Run comprehensive linting, type checking, and dependency analysis
    print(
        "\n🧹 Step 1: Running comprehensive linting, type checking, and dependency analysis"
    )
    print("🚀 Running pre-commit hooks (includes mypy and deptry)")
    c.run("uv run pre-commit run -a")

    # Step 2: Check uv lock file consistency
    print("\n🔍 Step 2: Checking uv lock file consistency")
    print("🚀 Checking uv lock file consistency with 'pyproject.toml'")
    c.run("uv lock --check")

    # Step 3: Run comprehensive test suite
    if not no_test:
        print("\n🧪 Step 3: Running comprehensive test suite")
        print("🚀 Running pytest with coverage")
        c.run(
            "uv run pytest --cov --cov-config=pyproject.toml --cov-report=html --cov-report=term --tb=no -qq"
        )

    print("\n" + "=" * 60)
    print("✅ Pre-release checks completed successfully!")
    print(
        "🎉 Repository is ready for release. You can now run 'invoke release' with the appropriate rule."
    )
    print("   Example: invoke release --rule=patch")


@task
def release(c, rule="", retry=False):
    """
    Create a new git tag and push it to the remote repository.

    This will create a new tag and push it to the remote repository, which will trigger
    a new build and deployment of the package to PyPI.

    Args:
        rule: Version bump rule (major, minor, patch, alpha, beta, rc, post, dev)
        retry: If True, force-push existing tags without creating new version (default: False)

    RULE        BEFORE  AFTER
    major       1.3.0   2.0.0
    minor       2.1.4   2.2.0
    patch       4.1.1   4.1.2
    alpha       1.0.2   1.0.3a1
    beta        1.0.3a1 1.0.3b1
    rc          1.0.3b1 1.0.3rc1
    stable      1.0.3rc1 1.0.3

    Examples:
        invoke release --rule=patch        # Bump patch version and release
        invoke release --retry             # Force-push existing tags (e.g., to retrigger CI)
    """
    # prerelease(c)
    # Get the current version number
    version_short = c.run("uv version --short", hide=True).stdout.strip()
    version = c.run("uv version", hide=True).stdout.strip()

    if retry:
        # retry existing tags without creating new version
        print(f"♻️  retrying existing tag v{version_short}...")
        response = (
            input(
                f"This will force-push tag v{version_short} to retrigger CI. Continue? (y/N): "
            )
            .strip()
            .lower()
        )
        if response not in ("y", "yes"):
            print("❌ retry cancelled.")
            return

        # Move the tag to the current HEAD (which includes any fixes committed since the failure)
        c.run(f"git tag -d v{version_short}", warn=True)
        c.run(f'git tag -a v{version_short} -m "{version}"')
        c.run(f"git push origin v{version_short} --force")

        # Push the branch — this is what actually triggers the Tests workflow,
        # which chains into Build, which chains into Release (where the tag is detected).
        # Pushing only the tag does not trigger Tests and the pipeline never starts.
        c.run("git push origin main")
        print(
            f"✅ Tag v{version_short} updated and main pushed — CI chain retriggered!"
        )
        return

    if not rule:
        print("❌ Error: You must specify a version bump rule.")
        print("   Example: invoke release --rule=patch")
        print(
            "\n   Available rules: major, minor, patch, stable, alpha, beta, rc, post, dev"
        )
        return

    # Check for unstaged changes
    unstaged_result = c.run("git diff --name-only", hide=True, warn=True)
    if unstaged_result.stdout.strip():
        print("⚠️  WARNING: You have unstaged changes:")
        print(unstaged_result.stdout)
        response = input("Continue with release? (y/N): ").strip().lower()
        if response not in ("y", "yes"):
            print("❌ Release cancelled.")
            return

    # Bump the current version using the specified rule
    c.run(f"uv version --bump {rule}")
    version_short = c.run("uv version --short", hide=True).stdout.strip()
    version = c.run("uv version", hide=True).stdout.strip()

    # Commit the version bump and any staged changes
    staged_result = c.run("git diff --cached --name-only", hide=True, warn=True)
    if staged_result.stdout.strip():
        print(f"🚀 Committing staged changes and version bump for v{version_short}")
        c.run(
            f'git add pyproject.toml uv.lock && git commit -m "Release v{version_short}"'
        )
    else:
        print(f"🚀 Committing version bump for v{version_short}")
        c.run(f'git commit pyproject.toml uv.lock -m "Release v{version_short}"')

    # Create an annotated tag
    c.run(f'git tag -a v{version_short} -m "{version}"')

    # Push commits and tags together
    print(f"📤 Pushing v{version_short} to remote repository...")
    c.run("git push origin main --follow-tags")

    print(f"✅ Release v{version_short} created and pushed successfully!")
    print("🎉 GitHub Actions will now build and publish the package to PyPI.")
