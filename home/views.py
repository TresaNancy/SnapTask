from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import login, authenticate,logout
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from datetime import datetime
from .models import Task
from django.http import JsonResponse
# from django import template

# register = template.Library()

# @register.filter(name='filter_tasks')
# def filter_tasks(tasks):
#     return tasks.filter(complete=False)


# Create your views here.
def home(request):
    return render(request,'home.html')

def signup(request):
    
    if request.method == 'POST':
        # Get form data from request
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = "+91" + request.POST['phone_number']
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']
        # Check if passwords match
        if password != repeat_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if len(password) < 6:
            messages.error(request, 'Password should be at least 6 characters long.')
            return redirect('signup')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, 'Password should contain at least one digit.')
            return redirect('signup')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, 'Password should contain at least one letter.')
            return redirect('signup')
        
        #checking if email already exists and if yes redirecting to signup
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,"Email is already registered. Please login with a different email")
            return redirect('signup')
        
        #checking if phone already exists and if yes redirecting to singup
        if CustomUser.objects.filter(phone=phone_number).exists():
            messages.error(request,"Phone Number is already registered with a different user. Please try with another number")
            return redirect('signup')

        # Create a new CustomUser object and save it
        try:
            user = CustomUser.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone_number,
            password=password
        )
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Please sign in.')
            return redirect('user_signin')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('signup')
    return render(request,'signup.html')


def user_signin(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')  # Using request.POST.get() to avoid KeyError
        password = request.POST.get('password')

        print("Email:", email)
        print("Password:", password)
        user = authenticate(request, email=email, password=password)
        try:
            print("hiiiii")
            print("request",request)
            print(email,password)
            user = authenticate(request, email=email, password=password)
            print(user)

            if user is not None:
                login(request, user)
                print("loged in.........")
                
                messages.success(request, 'You have successfully signed in.')
                return redirect('snaptask')  # Redirect to the home page or any other desired page after successful login
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        except Exception as e:
            # Handle authentication exceptions (e.g., AuthenticationFailed)
            messages.error(request, 'An error occurred during authentication.')

    return render(request, 'signin.html')

@never_cache
@login_required
def snaptask(request):
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user).order_by('-complete', '-last_updated')
        
        context = {'tasks' : tasks}
        
    return render(request,'snaptask.html',context)



@login_required(login_url='signin')
def add_task(request):
    if request.method == 'POST':
        name = request.POST.get('taskName')
        description = request.POST.get('taskDescription')
        date = request.POST.get('taskDate')

        # Perform basic validation
        if not name or not date:
            messages.error(request, 'Please fill in the required fields (Task Name and Date).')
            return redirect('snaptask')

        try:
            # Validate and parse date
            parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('snaptask')

        # Create and save the Task instance
        task = Task.objects.create(user=request.user, name=name, description=description, date=parsed_date)
        print("Task created:", task)
        messages.success(request, 'New task added')
        return redirect('snaptask')  # Redirect to a specific page after saving

    else:
        messages.error(request, 'Some issue occurred. Try after some time')

    return redirect('snaptask')

@never_cache
@login_required
def user_logout(request):
    logout(request)
    return render(request,'home.html')


@login_required(login_url='signin')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('snaptask')  # Redirect to a specific page after deleting

    return render(request, 'delete_task.html', {'task': task})



@login_required(login_url='signin')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        new_name = request.POST.get('task_name')
        new_description = request.POST.get('task_description')
        new_date = request.POST.get('task_date')

        # Check if new_name is provided before updating the task's name
        if new_name is not None:
            task.name = new_name

        # Update other task details
        task.description = new_description

        # Check if new_date is provided before updating the task's date
        if new_date is not None:
            try:
                parsed_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                task.date = parsed_date
            except ValueError:
                # Handle invalid date format
                # You may want to provide feedback to the user or take appropriate action
                pass

        # Save the updated task
        task.save()

        return redirect('snaptask')

    return redirect('snaptask')

@login_required(login_url='signin')
def update_task_status(request):
    if request.method == 'POST' and request.is_ajax():
        task_id = request.POST.get('task_id')
        complete = request.POST.get('complete')

        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.complete = (complete.lower() == 'true')
        task.save()

        return JsonResponse({'success': True, 'complete': task.complete})

    return JsonResponse({'success': False})


# def update_task_status(request):
#     if request.method == 'POST' and request.is_ajax():
#         task_id = request.POST.get('task_id')
#         complete = request.POST.get('complete')
        
#         # Validate inputs if necessary

#         task = get_object_or_404(Task, id=task_id, user=request.user)
#         task.complete = (complete.lower() == 'true')
#         task.save()

#         return JsonResponse({'success': True})

#     return JsonResponse({'success': False})


@login_required(login_url='signin')
def delete_all_tasks(request):
    if request.method == 'POST':
        # Get all tasks for the current user
        tasks = Task.objects.filter(user=request.user)
        
        # Delete all tasks
        tasks.delete()

        messages.success(request, 'All tasks deleted successfully.')
    
    return redirect('snaptask')  # Redirect to a specific page after deleting all tasks

@login_required(login_url='signin')
def complete_all_tasks(request):
    if request.method == 'POST':
        # Get all tasks for the current user
        tasks = Task.objects.filter(user=request.user)
        
        # Mark all tasks as completed
        tasks.update(complete=True)

        messages.success(request, 'All tasks marked as completed successfully.')
    
    return redirect('snaptask')  # Redirect to a specific page after completing all tasks