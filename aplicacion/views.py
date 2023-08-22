from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy

from .models import Curso, Profesor, Estudiante, Avatar
from .forms import CursoForm, ProfesorForm, \
                   RegistroUsuariosForm, UserEditForm, AvatarFormulario

from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth       import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, "aplicacion/home.html")

@login_required
def cursos(request):
    contexto = {'cursos': Curso.objects.all(), 'titulo': 'Reporte de Cursos', 'comisiones': ['55630', '55640'] }
    return render(request, "aplicacion/cursos.html", contexto)

@login_required
def profesores(request):
    return render(request, "aplicacion/profesores.html")

@login_required
def estudiantes(request):
    return render(request, "aplicacion/estudiantes.html")

@login_required
def entregables(request):
    return render(request, "aplicacion/entregables.html")

@login_required
def cursoForm(request):
    if request.method == "POST":
        curso = Curso(nombre=request.POST['nombre'], 
                      comision=request.POST['comision'])
        curso.save()
        return HttpResponse("Se grabo con exito el curso!")
    
    return render(request, "aplicacion/cursoForm.html")

@login_required
def cursoForm2(request):
    if request.method == "POST":
        miForm = CursoForm(request.POST)
        if miForm.is_valid():
            curso_nombre = miForm.cleaned_data.get('nombre')
            curso_comision = miForm.cleaned_data.get('comision')
            curso = Curso(nombre=curso_nombre,
                          comision=curso_comision)
            curso.save()
            return render(request, "aplicacion/base.html")
    else:
        miForm = CursoForm()
    
    return render(request, "aplicacion/cursoForm2.html", {"form": miForm })

@login_required
def buscarComision(request):
    return render(request, "aplicacion/buscarComision.html")

@login_required
def buscar2(request):
    if request.GET['buscar']:
        patron = request.GET['buscar']
        cursos = Curso.objects.filter(nombre__icontains=patron)
        contexto = {"cursos": cursos, 'titulo': f'Cursos que tiene como patron "{patron}"'}
        return render(request, "aplicacion/cursos.html", contexto)
    return HttpResponse("No se ingreso nada a buscar")

#___________________________ 15/08/2023

@login_required
def profesores(request):
    ctx = {'profesores': Profesor.objects.all()}
    return render(request, "aplicacion/profesores.html", ctx)

@login_required
def updateProfesor(request, id_profesor):
    profesor = Profesor.objects.get(id=id_profesor)
    if request.method == "POST":
        miForm = ProfesorForm(request.POST)
        if miForm.is_valid():
            profesor.nombre = miForm.cleaned_data.get('nombre')
            profesor.apellido = miForm.cleaned_data.get('apellido')
            profesor.email = miForm.cleaned_data.get('email')
            profesor.profesion = miForm.cleaned_data.get('profesion') 
            profesor.save()
            return redirect(reverse_lazy('profesores'))   
    else:
        miForm = ProfesorForm(initial={
            'nombre': profesor.nombre,
            'apellido': profesor.apellido,
            'email': profesor.email,
            'profesion': profesor.profesion,
        })
    return render(request, "aplicacion/profesorForm.html", {'form': miForm})

@login_required
def deleteProfesor(request, id_profesor):
    profesor = Profesor.objects.get(id=id_profesor)
    profesor.delete()
    return redirect(reverse_lazy('profesores'))

@login_required
def createProfesor(request):    
    if request.method == "POST":
        miForm = ProfesorForm(request.POST)
        if miForm.is_valid():
            p_nombre = miForm.cleaned_data.get('nombre')
            p_apellido = miForm.cleaned_data.get('apellido')
            p_email = miForm.cleaned_data.get('email')
            p_profesion = miForm.cleaned_data.get('profesion')
            profesor = Profesor(nombre=p_nombre, 
                             apellido=p_apellido,
                             email=p_email,
                             profesion=p_profesion,
                             )
            profesor.save()
            return redirect(reverse_lazy('profesores'))
    else:
        miForm = ProfesorForm()

    return render(request, "aplicacion/profesorForm.html", {"form":miForm})

#____________________ Class Based View

class EstudianteList(LoginRequiredMixin, ListView):
    model = Estudiante

class EstudianteCreate(LoginRequiredMixin, CreateView):
    model = Estudiante
    fields = ['nombre', 'apellido', 'email']
    success_url = reverse_lazy('estudiantes')

class EstudianteUpdate(LoginRequiredMixin, UpdateView):
    model = Estudiante
    fields = ['nombre', 'apellido', 'email']
    success_url = reverse_lazy('estudiantes')

class EstudianteDelete(LoginRequiredMixin, DeleteView):
    model = Estudiante
    success_url = reverse_lazy('estudiantes')

#__________________ Login / Logout / Registracion
# 
def login_request(request):
    if request.method == "POST":
        miForm = AuthenticationForm(request, data=request.POST)
        if miForm.is_valid():
            usuario = miForm.cleaned_data.get('username')
            password = miForm.cleaned_data.get('password')
            user = authenticate(username=usuario, password=password)
            if user is not None:
                login(request, user)

                try:
                    avatar = Avatar.objects.get(user=request.user.id).imagen.url
                except:
                    avatar = "/media/avatares/default.png"
                finally:
                    request.session["avatar"] = avatar

                return render(request, "aplicacion/base.html", {'mensaje': f'Bienvenido a nuestro sitio {usuario}'})
            else:
                return render(request, "aplicacion/login.html", {'form': miForm, 'mensaje': f'Los datos son inválidos'})
        else:
            return render(request, "aplicacion/login.html", {'form': miForm, 'mensaje': f'Los datos son inválidos'})

    miForm =   AuthenticationForm()      

    return render(request, "aplicacion/login.html", {"form":miForm})    

def register(request):
    if request.method == "POST":
        miForm = RegistroUsuariosForm(request.POST)
        if miForm.is_valid():
            usuario = miForm.cleaned_data.get('username')
            miForm.save()
            return render(request, "aplicacion/base.html")
    else:
        miForm =   RegistroUsuariosForm()      
    return render(request, "aplicacion/registro.html", {"form":miForm}) 

@login_required
def editarPerfil(request):
    usuario = request.user
    if request.method == "POST":
        form = UserEditForm(request.POST)
        if form.is_valid():
            usuario.email = form.cleaned_data.get('email')
            usuario.password1 = form.cleaned_data.get('password1')
            usuario.password2 = form.cleaned_data.get('password2')
            usuario.first_name = form.cleaned_data.get('first_name')
            usuario.last_name = form.cleaned_data.get('last_name')
            usuario.save()
            return render(request,"aplicacion/base.html")
        else:
            return render(request,"aplicacion/editarPerfil.html", {'form': form, 'usuario': usuario.username})
    else:
        form = UserEditForm(instance=usuario)
    return render(request, "aplicacion/editarPerfil.html", {'form': form, 'usuario': usuario.username})

@login_required
def agregarAvatar(request):
    if request.method == "POST":
        form = AvatarFormulario(request.POST, request.FILES) # Diferente a los forms tradicionales
        if form.is_valid():
            u = User.objects.get(username=request.user)

            # ____ Para borrar el avatar viejo
            avatarViejo = Avatar.objects.filter(user=u)
            if len(avatarViejo) > 0:
                for i in range(len(avatarViejo)):
                    avatarViejo[i].delete()

            # ____ Guardar el nuevo
            avatar = Avatar(user=u, imagen=form.cleaned_data['imagen'])
            avatar.save()

            # ___ Hago que la url de la imagen viaje en el request
            imagen = Avatar.objects.get(user=request.user.id).imagen.url
            request.session["avatar"] = imagen
            return render(request,"aplicacion/base.html")
    else:
        form = AvatarFormulario()
    return render(request, "aplicacion/agregarAvatar.html", {'form': form })


