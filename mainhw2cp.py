import Database
from _datetime import datetime
menu = '''\nPlease select one of the following options:
1. Add new customer
2. Remove customer
3. Search for customers
4. View late payments
5. Update last payment
6. Add/remove service or equipment
7. Change cost of service/equipment
8. Change bill amount due each month
9. Make a payment
10. EXIT

Your selection: '''
welcome = "Welcome to the Customer Tracking System!"

# adding customer
def prompt_add_customer():
    name = input("Customer name: ")
    customer_number = input("Customer number: ")
    return name, customer_number

# adding location
def prompt_add_location():
    address = input("Address: ")
    city = input("City: ")
    state = input("State: ")
    return address, city, state

# removing customer by id or name
def prompt_remove_customer():
    remove_by = input("Remove customer by (i)d or (n)ame? ")
    if remove_by.lower() == 'i':
        customer_id = input("Enter customer ID: ")
        rows_deleted = Database.remove_customer("customer_id", customer_id)
    elif remove_by.lower() == 'n':
        customer_name = input("Enter customer name: ")
        rows_deleted = Database.remove_customer("name", customer_name)
    else:
        print("Invalid option.")
        return

    if rows_deleted > 0:
        print(f"Customer removed successfully.")
    else:
        print("Customer not found.")

# Searching by name, id,  or location
def prompt_search_customers():
    search_type = input("Search by (n)ame, (i)d, or (l)ocation? ").lower()

    if search_type == 'n':
        name = input("Enter customer name: ")
        results = Database.search_customers_by_name(name)
        if results:
            print("Search Results:")
            for customer in results:
                print(f"ID: {customer[0]}, Name: {customer[1]}, Customer Number: {customer[2]}")
        else:
            print("No customers found with that name.")

    elif search_type == 'i':
        customer_id = input("Enter customer ID: ")
        results = Database.search_customer_by_id(customer_id)
        if results:
            print("Search Results:")
            for customer in results:
                print(f"ID: {customer[0]}, Name: {customer[1]}, Customer Number: {customer[2]}")
        else:
            print("No customers found with that ID.")

    elif search_type == 'l':
        location = input("Enter location (address): ")
        results = Database.search_customers_by_location(location)
        if results:
            print("Search Results:")
            for customer in results:
                print(f"ID: {customer[0]}, Name: {customer[1]}, Customer Number: {customer[2]}")
        else:
            print("No customers found at that location.")

    else:
        print("Invalid search type.")


# Late payment handling
def view_late_payments():
    late_payments = Database.get_late_payments()  # gets late payments from the database

    if late_payments:
        print("Late Payments:")
        for payment in late_payments:
            payment_id, customer_name, due_date = payment
            print(f"Payment ID: {payment_id}, Customer: {customer_name}, Due Date: {due_date}")
    else:
        print("No late payments found.")


# Update last payment/
def prompt_update_last_payment():
    # List all customers
    customers = Database.get_all_customers() # grabs every customer
    if not customers:
        print("No customers found.")
        return

    print("Select a customer to update the last payment:")
    for customer in customers:
        print(f"ID: {customer[0]}, Name: {customer[1]}")

    customer_id = input("Enter customer ID: ")

    # Fetch current last payment information for the selected customer
    billing_info = Database.get_billing_info(customer_id)  # Use the existing function to get billing info
    if not billing_info:
        print("No billing information found for this customer.")
        return

    current_payment_date = billing_info[1]
    print(f"Current last payment date: {current_payment_date}")

    # Prompt for the new last payment date
    new_payment_date = input("Enter the new last payment date (YYYY-MM-DD): ")

    # Update the last payment date in the database
    rows_updated = Database.update_last_payment_date(customer_id, new_payment_date)
    if rows_updated > 0:
        print("Last payment date updated successfully.")
    else:
        print("Failed to update last payment date.")

# adding service
# fixed service costs/ rates
def prompt_add_service():
    # Prompt for service name
    service_name = input("Enter service name: ")
    fixed_cost = Database.get_fixed_service_cost(service_name)  # Get the fixed cost

    if fixed_cost is None:
        print("Service not recognized or fixed cost not defined.")
        return

    # List existing customers
    customers = Database.get_all_customers()  # New function to fetch customers
    if not customers:
        print("No customers found.")
        return

    print("Select an existing customer:")
    for customer in customers:
        print(f"ID: {customer[0]}, Name: {customer[1]}")  # customer tuple format is (id, name)

    customer_id = input("Enter customer ID to add the service to: ")

    # List existing locations for the selected customer
    locations = Database.get_locations_for_customer(customer_id)  # New function to fetch locations for a customer
    if not locations:
        print("No locations found for this customer.")
        return

    print("Select an existing location:")
    for location in locations:
        print(f"ID: {location[0]}, Address: {location[1]}")

    location_id = input("Enter location ID to link the service to: ")

    # Add the service to the database
    service_id = Database.add_service(service_name, fixed_cost)
    print(f"Added service successfully with ID: {service_id}")

    # Link the service to the customer and location
    customer_service_id = Database.add_customer_service(customer_id, location_id, service_id)
    print(f"Linked service to customer at location with ID: {customer_service_id}")


# remove service
def prompt_remove_service():
    customer_id = input("Enter customer ID to remove service from: ")
    service_id = input("Enter service ID to remove: ")
    location_id = input("Enter location ID from which to remove service: ")
    confirmation = input(f"Are you sure you want to remove service{service_id}? (y/n):")
    if confirmation.lower() == 'y':
        row_del = Database.remove_customer_service(customer_id, service_id, location_id)
        if row_del > 0:
            print(f"Service removed successfully.")
        else:
            print("Service not found.")
    else:
        print("Good day")


def prompt_change_service_cost():
    service_id = input("Enter the service ID to change: ")
    new_cost = input("Enter the new cost for the service: ")

    rows_updated = Database.update_service_cost(service_id, new_cost)

    if rows_updated > 0:
        print("Service cost updated successfully.")
    else:
        print("Service not found or cost not updated.")


def prompt_change_equipment_cost():
    equipment_id = input("Enter the equipment ID to change: ")
    new_cost = input("Enter the new cost for the equipment: ")

    # Call the database function to update the cost
    rows_updated = Database.update_equipment_cost(equipment_id, new_cost)

    if rows_updated > 0:
        print("Equipment cost updated successfully.")
    else:
        print("Equipment not found or cost not updated.")


def prompt_change_bill_amount():
    # List all customers
    customers = Database.get_all_customers()  # Use the existing function to fetch customers
    if not customers:
        print("No customers found.")
        return

    print("Select a customer to change the billing amount:")
    for customer in customers:
        print(f"ID: {customer[0]}, Name: {customer[1]}")  # customer tuple format is (id, name)

    customer_id = input("Enter customer ID: ")

    # Fetch current billing information for the selected customer
    billing_info = Database.get_billing_info(customer_id)  # New function to get billing info
    if not billing_info:
        print("No billing information found for this customer.")
        return

    current_amount = billing_info[0]  
    print(f"Current billing amount due: {current_amount}")

    # Prompt for the new billing amount
    new_amount = input("Enter the new billing amount due: ")

    # Update the billing amount in the database
    rows_updated = Database.update_last_payment_date(customer_id, new_amount)  # New function to update billing
    if rows_updated > 0:
        print("Billing amount updated successfully.")
    else:
        print("Failed to update billing amount.")

# payment function to feed into billing table
def prompt_make_payment():
    customers = Database.get_all_customers()  # Get the list of all customers
    if not customers:
        print("No customers found.")
        return

    print("Select a customer to make a payment:")
    for customer in customers:
        print(f"ID: {customer[0]}, Name: {customer[1]}")

    # Get customer ID from user input
    customer_id = input("Enter the customer ID to make a payment: ")

    # Get customer billing info
    billing_info = Database.get_billing_info(customer_id)
    if not billing_info:
        print("No billing information found for this customer.")
        return

    # Display billing info to user
    print(f"Amount due: {billing_info[1]}, Due date: {billing_info[2]}")

    # Get payment details from the user
    amount_paid = float(input("Enter the amount you are paying: "))
    credit_card_number = input("Enter your credit card number: ")

    # Ensure payment is not exceeding the due amount
    if amount_paid > (billing_info[1]):
        print("Payment exceeds the amount due. Please enter a valid amount.")
        return

    # Record the payment
    Database.make_payment(customer_id, amount_paid, credit_card_number)

    # Update the billing table after payment
    Database.update_billing(customer_id, amount_paid)

    print("Payment recorded successfully.")

def prompt_add_billing():
    customer_id = input("Enter customer ID: ")
    due_date = input("Enter the due date (YYYY-MM-DD): ")
    amount_due = float(input("Enter the amount due: "))
    last_payment_date = input("Enter the last payment date (YYYY-MM-DD) or leave blank: ")
    last_payment_date = last_payment_date if last_payment_date else None
    is_late = int(input("Is the payment late? (1 for yes, 0 for no): "))
    credit_card_number = input("Enter the credit card number: ")

    billing_id = Database.add_billing(customer_id, due_date, amount_due, last_payment_date, is_late, credit_card_number)
    print(f"Added billing record with ID: {billing_id}")


print("Welcome")
Database.create_tables()




while (user_input := input(menu)) != "10":
    if user_input == "1":
        name, customer_number = prompt_add_customer()
        customer_id = Database.add_customer(name, customer_number)
        print(f"Added customer with ID: {customer_id}")
        add_location = input("Add a location for this customer? (y/n): ")
        if add_location.lower() == 'y':
            address, city, state = prompt_add_location()
            location_id = Database.add_location(customer_id, address, city, state)
            print(f"Added location with ID: {location_id}")
        else:
            print("OK")


    elif user_input == "2":
        prompt_remove_customer()

    elif user_input == "3":
       prompt_search_customers()

    elif user_input == "4":
        view_late_payments()
        pass
    elif user_input == "5":
        prompt_update_last_payment()
        pass
    elif user_input == "6":
        del_or_add_service = input("Will you be (a)dding or (d)eleting a service today? (a/d): ")
        if del_or_add_service.lower() == 'a':
            prompt_add_service()
        else:
            prompt_remove_service()

    elif user_input == "7":
        change_type = input("Are you changing the cost of (s)ervice or (e)quipment? ").lower()
        if change_type == 's':
            prompt_change_service_cost()
        elif change_type == 'e':
            prompt_change_equipment_cost()
        else:
            print("Invalid option.")

    elif user_input == "8":
        prompt_change_bill_amount()
    elif user_input == "9":
        payment_options = input("Would you like to make a payment? (y/n): ")
        if payment_options.lower() == 'y':
            prompt_make_payment()
        elif payment_options.lower() == 'n':
            prompt_add_billing()
        else:
            print("Invalid option.")
    else:
        print("Invalid input, please try again.")