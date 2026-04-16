'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import api from '@/lib/api';
import { ProjectSchema, ProjectCreateSchema } from '@/lib/schemas';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';  // Import sonner for notifications

export default function Projects() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!isLoading && !user) router.push('/login');
  }, [user, isLoading, router]);

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const res = await api.get('projects/');
      return z.array(ProjectSchema).parse(res.data);
    },
    enabled: !!user,
  });

  const form = useForm<z.infer<typeof ProjectCreateSchema>>({
    resolver: zodResolver(ProjectCreateSchema),
    defaultValues: {
      name: '',
      description: '',
      start_date: new Date().toISOString().split('T')[0],
      end_date: null,
      team_id: null,
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: z.infer<typeof ProjectCreateSchema>) => {
      const res = await api.post('projects/', data);
      return ProjectSchema.parse(res.data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      form.reset();
      toast.success('Project created successfully');  // Use sonner toast
    },
    onError: () => toast.error('Failed to create project'),  // Use sonner toast
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => api.delete(`projects/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project deleted successfully');  // Use sonner toast
    },
    onError: () => toast.error('Failed to delete project'),  // Use sonner toast
  });

  const onSubmit = (data: z.infer<typeof ProjectCreateSchema>) => createMutation.mutate(data);

  if (isLoading || projectsLoading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>;

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-2xl font-bold">Projects</CardTitle>
          <Dialog>
            <DialogTrigger asChild>
              <Button>Create New Project</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create Project</DialogTitle>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Project name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Input placeholder="Project description" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="start_date"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Start Date</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="end_date"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>End Date (optional)</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} value={field.value || ''} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  {/* Add team_id when teams are implemented */}
                  <Button type="submit" className="w-full">Create Project</Button>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Owner</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects?.map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.description}</TableCell>
                  <TableCell>{project.start_date}</TableCell>
                  <TableCell>{project.end_date || 'Ongoing'}</TableCell>
                  <TableCell>{project.owner.username}</TableCell>
                  <TableCell>
                    <Button variant="ghost" onClick={() => router.push(`/projects/${project.id}`)}>View Tasks</Button>
                    <Button variant="destructive" onClick={() => deleteMutation.mutate(project.id)}>Delete</Button>
                  </TableCell>
                </TableRow>
              ))}
              {projects?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center">No projects yet. Create one to get started.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}