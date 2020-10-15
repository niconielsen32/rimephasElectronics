import dispenser           #dispenser.py
import stattracker         #stattracker.py
import keyboard
import csv
import pygame

pygame.init()




if __name__ == '__main__':
    

    window = pygame.display.set_mode((800,480), pygame.DOUBLEBUF)
    screen = pygame.display.get_surface()
    
    # Initialize dispenser
    dispenser = dispenser.Dispenser()
    dispenser.init_GPIO()
    
    # Initialize stats variables
    stats = stattracker.StatTracker()
    
    
    
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    print("Terminating program")
                if event.key == pygame.K_p:
                    plot_data, plot_size = stats.get_plot()
                    plot = pygame.image.fromstring(plot_data, plot_size, "RGB")
                    screen.blit(plot, (0,0))
                    pygame.display.flip()
                    print("Plotting data")
                if event.key == pygame.K_a:
                    dispenser.numberOfActivations += 1
                    print("Activations: ", dispenser.numberOfActivations)
                if event.key == pygame.K_o:
                    with open('dataDispenser.csv', 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(stats.hoursList)
                        writer.writerow(stats.activationsList)
                        print("Writing to CSV file")
                
        
        stats.update_plot(dispenser.numberOfActivations)
        dispenser.update()
        
            
    dispenser.cleanup()
    pygame.display.quit()
    pygame.quit()