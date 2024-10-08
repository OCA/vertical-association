# Installation

```
pip3 install python-gitlab
```

# Configure

1. Create a personal access token in Gitlab here
   https://gitlab.com/-/profile/personal_access_tokens;
2. go to `Settings` > `Technical` > `Gitlab Connections` in Odoo and copy/paste the
   token;
3. test the connection;
4. go to Projects;
5. on the project form set `Gitlab Fullname` to e.g. `inkscape/inkscape` and the Gitlab
   connection you just created;
6. on member / partner form set `Gitlab Username` and `Gitlab Email` (Email is used for
   reconciling commits)

# Usage

Activity will be imported every day, or you can manually run the scheduled action
(Membership: Import Gitlab activity)

If you imported Gitlab activity but some members were not configured correctly you can
re-reconcile activity to members by going to the tree view of membership activities,
select the activities you want to reconcile, and click `Reconcile Activity with Members`
in the action menu. Note that Odoo will say it selected all records but this will not be
the case as the max is 20k records.
