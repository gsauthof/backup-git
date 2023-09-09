This repository contains backup-git.py - a script for mirroring
a bunch of remote git repositories.

Example:

    backup-git.py --list repo.lst  --gh-starred juser --gl-starred jdoe

This invocation reads git repository clone URLs from the file
`repo.lst`, fetches more repository clone URLs from all the
starred repositories of the specified user and clones (or pulls)
those repositories locally.

It creates a simple directory hierarchy in the current working
directory using the `$hostname/$user/$repo` pattern, such as:

```
── gitea.sysmocom.de
│   └── odoo
│       └── python-inema.git
├── github.com
│   ├── AntennaPod
│   │   └── AntennaPod.git
│   ├── Backblaze
│   │   └── B2_Command_Line_Tool.git
│   ├── EnterpriseQualityCoding
│   │   └── FizzBuzzEnterpriseEdition.git
│   ├── FortAwesome
│   │   └── Font-Awesome.git
[..]
├── gitlab.com
│   ├── cryptsetup
│   │   └── cryptsetup.git
│   ├── fdroid
│   │   └── fdroidclient.git
│   ├── gnutls
[..]
```

NB: As of 2023, the Github and Gitlab APIs allow to fetch the
list of all starred repositories such that there is NO need to
configure any API keys.

## Backup Considerations

Keep in mind that an upstream repository might have its history
rewritten (e.g. by a force push) and backup-git.py doesn't try to
detect this, i.e. it just mirrors those changes, as any other
upstream change.

It thus makes sense to operate backup-git.py on a
snapshot-capable filesystem such as Btrfs or ZFS and have some
snapshot schedule configured for that volume.
Alternatively, you may want to snapshot the backup-git.py working
directory via a generic backup tool such as restic.

That way you have the option to go back to an earlier snapshot
of that repository mirror directory tree and look at a git
repository's history from there.


## Dependencies

The script depends on the following extra python packages:

- [configargparse](https://github.com/bw2/ConfigArgParse)
- [github](https://github.com/PyGithub/PyGithub)
- [gitlab](https://github.com/python-gitlab/python-gitlab)

On Fedora you can install them like this:

```
dnf install python3-configargparse python3-pygithub python3-gitlab
```

## Cron Job

When running it as a Cron job it makes sense to wrap the command
with the [silence][silence] utility (or similar) to retain the output in
case of any error but discard it in the good case.

## License

It's licensed under the GPLv3+.



[silence]: https://github.com/gsauthof/utility/#silence
