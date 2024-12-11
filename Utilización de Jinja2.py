from flask import Flask, render_template, request, redirect, url_for
import redis

# Configuración de Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Crear la aplicación Flask
app = Flask(__name__)

# Rutas de la aplicación

@app.route('/')
def index():
    # Mostrar un formulario para agregar una nueva receta
    return render_template('index.html')

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    # Obtener los datos del formulario
    name = request.form['name']
    ingredients = request.form['ingredients'].split(',')
    steps = request.form['steps'].split('.')

    # Guardar la receta en Redis
    recipe_data = {
        "ingredients": ingredients,
        "steps": steps
    }
    redis_client.set(name, str(recipe_data))

    # Redirigir a la página principal
    return redirect(url_for('index'))

@app.route('/list_recipes')
def list_recipes():
    # Obtener todas las recetas de Redis
    recipes = redis_client.keys()
    return render_template('list_recipes.html', recipes=recipes)

@app.route('/view_recipe/<recipe_name>')
def view_recipe(recipe_name):
    # Obtener una receta específica
    recipe_data = redis_client.get(recipe_name)
    if recipe_data:
        recipe_data = eval(recipe_data)
        return render_template('view_recipe.html', recipe=recipe_data)
    else:
        return "Receta no encontrada"

@app.route('/update_recipe/<recipe_name>', methods=['POST'])
def update_recipe(recipe_name):
    # Obtener los nuevos datos de la receta
    new_name = request.form['name']
    new_ingredients = request.form['ingredients'].split(',')
    new_steps = request.form['steps'].split('.')

    # Actualizar la receta en Redis
    recipe_data = redis_client.get(recipe_name)
    if recipe_data:
        recipe_data = eval(recipe_data)
        if new_name:
            redis_client.delete(recipe_name)
            recipe_name = new_name
        if new_ingredients:
            recipe_data["ingredients"] = new_ingredients
        if new_steps:
            recipe_data["steps"] = new_steps
        redis_client.set(recipe_name, str(recipe_data))
        return redirect(url_for('list_recipes'))
    else:
        return "Receta no encontrada"

@app.route('/delete_recipe/<recipe_name>')
def delete_recipe(recipe_name):
    # Eliminar una receta de Redis
    redis_client.delete(recipe_name)
    return redirect(url_for('list_recipes'))

if __name__ == '__main__':
    app.run(debug=True)