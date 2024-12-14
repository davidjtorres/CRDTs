# Use an official Node.js runtime as a parent image
FROM node:20.0.0

# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies using Yarn
RUN yarn install

# Copy the rest of the application code 
COPY . .

# Build the React app
RUN yarn build

# Expose the port the app runs on
EXPOSE 3000

# Start the React app
CMD ["yarn", "start"]