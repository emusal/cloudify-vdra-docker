from cloudify.workflows import ctx
from cloudify.workflows import parameters as p

for node in ctx.nodes:
    for instance in node.instances:
        outstr=instance.id
        if instance.id.startswith('EM') == False:
           continue

        instance.execute_operation('uangel.provision', kwargs={
            'em_value': p.em_value
        })
        outstr=instance.id
        with open("/tmp/log","a") as f:
           f.write("\n provision_em.py instance %s" %(outstr))
