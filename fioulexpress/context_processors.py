from models import Config

def config_processor(request):
    return {'config' : Config.objects.filter(actif=True)[0]}