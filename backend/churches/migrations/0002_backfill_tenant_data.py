# Données existantes : une Church par National + propagation church_id.

from django.db import migrations # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils


def forwards(apps, schema_editor):
    Church = apps.get_model('churches', 'Church')
    Subscription = apps.get_model('churches', 'Subscription')
    National = apps.get_model('hierarchy', 'National')
    Region = apps.get_model('hierarchy', 'Region')
    District = apps.get_model('hierarchy', 'District')
    Paroisse = apps.get_model('hierarchy', 'Paroisse')
    EgliseLocale = apps.get_model('hierarchy', 'EgliseLocale')
    User = apps.get_model('accounts', 'User')
    Fidele = apps.get_model('members', 'Fidele')
    Ministere = apps.get_model('members', 'Ministere')
    TransfertFidele = apps.get_model('members', 'TransfertFidele')
    Cotisation = apps.get_model('contributions', 'Cotisation')
    Recu = apps.get_model('contributions', 'Recu')
    ObjectifCotisation = apps.get_model('contributions', 'ObjectifCotisation')
    Evenement = apps.get_model('events', 'Evenement')
    Annonce = apps.get_model('events', 'Annonce')
    InscriptionEvenement = apps.get_model('events', 'InscriptionEvenement')
    Notification = apps.get_model('notifications', 'Notification')
    AuditLog = apps.get_model('accounts', 'AuditLog')

    today = timezone.now().date()

    for national in National.objects.all():
        if national.church_id:
            ch = Church.objects.get(pk=national.church_id)
        else:
            ch = Church.objects.create(
                name=national.nom or 'Organisation',
                email=(national.email or 'contact@localhost.local'),
                phone=national.telephone or '',
            )
            national.church_id = ch.pk
            national.save(update_fields=['church_id'])
        Subscription.objects.get_or_create(
            church=ch,
            defaults={
                'plan': 'free',
                'is_active': True,
                'start_date': today,
            },
        )

    if not Church.objects.exists():
        ch = Church.objects.create(
            name='Organisation par défaut',
            email='admin@localhost.local',
            phone='',
        )
        National.objects.create(
            church=ch,
            nom=ch.name,
            pays='',
            email=ch.email,
            telephone=ch.phone,
        )
        Subscription.objects.create(church=ch, plan='free', is_active=True, start_date=today)

    for r in Region.objects.filter(church__isnull=True):
        nat = National.objects.filter(pk=r.national_id).first()
        if nat and nat.church_id:
            r.church_id = nat.church_id
            r.save(update_fields=['church_id'])

    for d in District.objects.filter(church__isnull=True):
        reg = Region.objects.filter(pk=d.region_id).first()
        if reg and reg.church_id:
            d.church_id = reg.church_id
            d.save(update_fields=['church_id'])

    for p in Paroisse.objects.filter(church__isnull=True):
        dist = District.objects.filter(pk=p.district_id).first()
        if dist and dist.church_id:
            p.church_id = dist.church_id
            p.save(update_fields=['church_id'])

    for e in EgliseLocale.objects.filter(church__isnull=True):
        par = Paroisse.objects.filter(pk=e.paroisse_id).first()
        if par and par.church_id:
            e.church_id = par.church_id
            e.save(update_fields=['church_id'])

    default_church = Church.objects.order_by('pk').first()
    for u in User.objects.filter(church__isnull=True):
        if getattr(u, 'role', '') == 'super_admin':
            continue
        u.church_id = default_church.pk
        u.save(update_fields=['church_id'])

    for m in Ministere.objects.filter(church__isnull=True):
        egl = EgliseLocale.objects.filter(pk=m.eglise_id).first()
        if egl and egl.church_id:
            m.church_id = egl.church_id
            m.save(update_fields=['church_id'])

    for f in Fidele.objects.filter(church__isnull=True):
        egl = EgliseLocale.objects.filter(pk=f.eglise_id).first()
        if egl and egl.church_id:
            f.church_id = egl.church_id
            f.save(update_fields=['church_id'])

    for t in TransfertFidele.objects.filter(church__isnull=True):
        if t.fidele_id:
            fd = Fidele.objects.filter(pk=t.fidele_id).first()
            if fd and fd.church_id:
                t.church_id = fd.church_id
                t.save(update_fields=['church_id'])

    for c in Cotisation.objects.filter(church__isnull=True):
        ch_id = None
        if c.fidele_id:
            fd = Fidele.objects.filter(pk=c.fidele_id).first()
            if fd:
                ch_id = fd.church_id
        if not ch_id and c.enregistre_par_id:
            u = User.objects.filter(pk=c.enregistre_par_id).first()
            if u:
                ch_id = u.church_id
        if ch_id:
            c.church_id = ch_id
            c.save(update_fields=['church_id'])

    for rec in Recu.objects.filter(church__isnull=True):
        cot = Cotisation.objects.filter(pk=rec.cotisation_id).first()
        if cot and cot.church_id:
            rec.church_id = cot.church_id
            rec.save(update_fields=['church_id'])

    for o in ObjectifCotisation.objects.filter(church__isnull=True):
        o.church_id = default_church.pk
        o.save(update_fields=['church_id'])

    for ev in Evenement.objects.filter(church__isnull=True):
        if ev.createur_id:
            u = User.objects.filter(pk=ev.createur_id).first()
            if u and u.church_id:
                ev.church_id = u.church_id
                ev.save(update_fields=['church_id'])
        elif default_church:
            ev.church_id = default_church.pk
            ev.save(update_fields=['church_id'])

    for a in Annonce.objects.filter(church__isnull=True):
        if a.auteur_id:
            u = User.objects.filter(pk=a.auteur_id).first()
            if u and u.church_id:
                a.church_id = u.church_id
                a.save(update_fields=['church_id'])
        elif default_church:
            a.church_id = default_church.pk
            a.save(update_fields=['church_id'])

    for ins in InscriptionEvenement.objects.filter(church__isnull=True):
        ev = Evenement.objects.filter(pk=ins.evenement_id).first()
        if ev and ev.church_id:
            ins.church_id = ev.church_id
            ins.save(update_fields=['church_id'])

    for n in Notification.objects.filter(church__isnull=True):
        u = User.objects.filter(pk=n.destinataire_id).first()
        if u and u.church_id:
            n.church_id = u.church_id
            n.save(update_fields=['church_id'])

    for log in AuditLog.objects.filter(church__isnull=True):
        if log.user_id:
            u = User.objects.filter(pk=log.user_id).first()
            if u and u.church_id:
                log.church_id = u.church_id
                log.save(update_fields=['church_id'])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('churches', '0001_initial'),
        ('hierarchy', '0002_alter_district_unique_together_and_more'),
        ('accounts', '0002_auditlog_church_user_church_alter_user_role'),
        ('members', '0002_fidele_church_ministere_church_and_more'),
        ('contributions', '0002_alter_objectifcotisation_unique_together_and_more'),
        ('events', '0002_annonce_church_evenement_church_and_more'),
        ('notifications', '0002_notification_church'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
