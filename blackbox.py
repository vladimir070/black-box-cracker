import random

# Загадочная функция (мы не знаем ее код)
def mysterious_function(input_data):
    """Это загадочная функция, с разными вероятностями для каждого типа."""
    state_probabilities = {"int": 0.2, "str": 0.5, "list": 0.2, "none": 0.1}
    state = random.choices(list(state_probabilities.keys()), weights=list(state_probabilities.values()), k=1)[0]
    if isinstance(input_data, int) and state == "int":
        return input_data * random.randint(1, 10)
    elif isinstance(input_data, str) and state == "str":
        return input_data.upper() + "!"
    elif isinstance(input_data, list) and state == "list":
        return [x * 2 for x in input_data]
    else:
        return None

# Параметры генетического алгоритма (адаптивные)
INITIAL_POPULATION_SIZE = 50
MUTATION_RATE = 0.1
NUM_GENERATIONS = 100
TYPE_CORRECT_BOOST = 2.0 # Насколько повышаем пригодность, если правильно угадали тип
WRONG_TYPE_PENALTY = 0.1 # Штраф за неправильный тип данных
ADAPTIVE_MUTATION_DECREASE = 0.95 # Уменьшаем мутацию, если прогресс есть
ADAPTIVE_MUTATION_INCREASE = 1.05 # Увеличиваем, если прогресса нет
ADAPTIVE_POPULATION_INCREASE = 1.1 # Увеличиваем популяцию, если всё плохо
MIN_POPULATION_SIZE = 20
MAX_POPULATION_SIZE = 200

# Функция для оценки пригодности (fitness)
def calculate_fitness(input_data, target_result, function):
    """Оценивает, насколько входные данные соответствуют целевому результату."""
    try:
        result = function(input_data)
        type_fitness = 1.0 # Базовая пригодность по типу данных
        if isinstance(input_data, int) and isinstance(target_result, int):
            type_fitness = TYPE_CORRECT_BOOST
        elif isinstance(input_data, str) and isinstance(target_result, str):
            type_fitness = TYPE_CORRECT_BOOST
        elif isinstance(input_data, list) and isinstance(target_result, list):
            type_fitness = TYPE_CORRECT_BOOST
        else:
            type_fitness = WRONG_TYPE_PENALTY

        result_fitness = 0.0 # Пригодность по значению результата
        if result == target_result:
            result_fitness = float('inf')
        elif isinstance(result, int) and isinstance(target_result, int):
            result_fitness = 1.0 / (abs(result - target_result) + 1)
        elif isinstance(result, str) and isinstance(target_result, str):
            common_chars = sum(1 for a, b in zip(result, target_result) if a == b)
            result_fitness = float(common_chars) / len(target_result)
        elif isinstance(result, list) and isinstance(target_result, list):
            common_elements = sum(1 for a, b in zip(result, target_result) if a == b)
            result_fitness = float(common_elements) / len(target_result)

        return type_fitness * result_fitness # Итоговая пригодность

    except TypeError:
        return 0.0

# Функция для генерации случайных входных данных (геном)
def generate_random_genome(input_type):
    """Генерирует случайный геном (входные данные) для заданного типа."""
    if input_type == "int": return random.randint(-100, 100)
    elif input_type == "str": return ''.join(random.choice('abcdefg') for _ in range(random.randint(3, 10)))
    elif input_type == "list": return [random.randint(-10, 10) for _ in range(random.randint(2, 5))]
    else: return None

# Адаптивные функции мутации
def mutate_genome(genome, input_type):
    """Мутирует геном, адаптируя диапазон мутации к прогрессу."""
    mutation_range = 5 # Для int
    if input_type == "int": return genome + random.randint(-mutation_range, mutation_range)
    elif input_type == "str":
        index = random.randint(0, len(genome) - 1)
        return genome[:index] + random.choice('abcdefg') + genome[index+1:]
    elif input_type == "list":
        index = random.randint(0, len(genome) - 1)
        genome[index] += random.randint(-2, 2)
        return genome
    else: return genome

# Функция для скрещивания (кроссинговера)
def crossover_genomes(genome1, genome2, input_type):
    """Скрещивает два генома."""
    if input_type == "int": return (genome1 + genome2) // 2
    elif input_type == "str":
        crossover_point = random.randint(1, min(len(genome1), len(genome2)) - 1)
        return genome1[:crossover_point] + genome2[crossover_point:]
    elif input_type == "list":
        crossover_point = random.randint(1, min(len(genome1), len(genome2)) - 1)
        return genome1[:crossover_point] + genome2[crossover_point:]
    else: return genome1

# Основная функция генетического алгоритма
def genetic_algorithm(function, target_result, input_type="any"):
    """Применяет генетический алгоритм для поиска входных данных."""

    population_size = INITIAL_POPULATION_SIZE # Динамический размер популяции
    mutation_rate = MUTATION_RATE # Динамическая скорость мутации

    # 1. Инициализация популяции
    population = [genome for _ in range(population_size) if (genome := generate_random_genome(input_type)) is not None]
    best_fitness_history = [] # История лучших результатов для адаптации
    last_improvement = 0 # Номер поколения, когда было последнее улучшение

    # 2. Эволюция
    for generation in range(NUM_GENERATIONS):
        # 2.1. Оценка пригодности (fitness)
        fitness_scores = [calculate_fitness(genome, target_result, function) for genome in population]
        best_fitness = max(fitness_scores)

        # 2.2. Отбор (selection) - турнирный отбор (улучшенный)
        selected_genomes = []
        for _ in range(population_size):
            # Выбираем K случайных родителей и выбираем лучшего.
            K = 3 # Турнирный размер. Больше K = строже отбор.
            tournament = random.choices(range(len(population)), k=K)
            winner = max(tournament, key=lambda i: fitness_scores[i])
            selected_genomes.append(population[winner])

        # 2.3. Адаптация скорости мутации и размера популяции
        if best_fitness == float('inf'): # Нашли идеальное решение
            print(f"Успех! Найдено идеальное решение на поколении {generation+1}.")
            break
        elif generation > 5:  # Начинаем адаптацию после нескольких поколений
            if best_fitness > (sum(best_fitness_history[-5:]) / 5): # Был прогресс
                mutation_rate *= ADAPTIVE_MUTATION_DECREASE
                last_improvement = generation
            else:  # Прогресса не было
                mutation_rate *= ADAPTIVE_MUTATION_INCREASE
        if (generation - last_improvement) > 20: # Если долго нет прогресса, увеличиваем популяцию
            population_size = min(population_size * ADAPTIVE_POPULATION_INCREASE, MAX_POPULATION_SIZE)
            print(f"Увеличение популяции до {population_size}.")
            last_improvement = generation # Считаем, что увеличение популяции - улучшение

        mutation_rate = max(0.01, min(mutation_rate, 0.5)) # Ограничиваем скорость мутации
        population_size = max(MIN_POPULATION_SIZE, int(population_size)) # Ограничиваем размер популяции
        best_fitness_history.append(best_fitness)  # Сохраняем лучшую пригодность

        # 2.4. Скрещивание и мутация (с учетом адаптивной скорости)
        new_population = []
        for i in range(0, population_size, 2):
            parent1 = selected_genomes[i % len(selected_genomes)]
            parent2 = selected_genomes[(i + 1) % len(selected_genomes)]
            child1 = crossover_genomes(parent1, parent2, input_type)
            child2 = crossover_genomes(parent2, parent1, input_type)

            if random.random() < mutation_rate: child1 = mutate_genome(child1, input_type)
            if random.random() < mutation_rate: child2 = mutate_genome(child2, input_type)
            new_population.extend([child1, child2])
        population = new_population[:population_size] # Обрезаем до нужного размера

        print(f"Поколение {generation + 1}: Лучшая пригодность = {best_fitness:.4f}, Мутация = {mutation_rate:.3f}, Популяция = {population_size}")

    # 3.  Вывод результата
    best_genome = population[fitness_scores.index(max(fitness_scores))]
    result = function(best_genome)
    print("\nПоиск завершен.")
    print(f"Лучшие входные данные: Тип: {type(best_genome)}, Вход: {best_genome}, Результат: {result}")
    print(f"Пригодность: {max(fitness_scores):.4f}")

# Пример использования
target_result = "HELLO!"
genetic_algorithm(mysterious_function, target_result, input_type="str")

target_result = [4, 4, 4]
genetic_algorithm(mysterious_function, target_result, input_type="list")

target_result = 25
genetic_algorithm(mysterious_function, target_result, input_type="int")